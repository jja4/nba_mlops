# NBA MLOps → GCP Terraform - Quick Reference Card

## 📋 Manual Setup Commands (Phase 1)

```bash
# Set variables
export PROJECT_ID="nba-mlops-prod"
export GCP_REGION="europe-west3"

# 1. Create project
gcloud projects create $PROJECT_ID --name="NBA MLOps Production"
gcloud config set project $PROJECT_ID

# 2. Enable APIs
gcloud services enable run.googleapis.com sqladmin.googleapis.com \
  storage.googleapis.com artifactregistry.googleapis.com \
  secretmanager.googleapis.com monitoring.googleapis.com \
  logging.googleapis.com compute.googleapis.com

# 3. Create Terraform service account
gcloud iam service-accounts create terraform-sa \
  --display-name="Terraform Service Account"

# 4. Grant roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:terraform-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/editor"

# 5. Create key
gcloud iam service-accounts keys create terraform-key.json \
  --iam-account=terraform-sa@${PROJECT_ID}.iam.gserviceaccount.com

export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/terraform-key.json"

# 6. Create secret
echo -n "your-password" | gcloud secrets create db-password --data-file=-

# 7. Build & push Docker images
gcloud auth configure-docker ${GCP_REGION}-docker.pkg.dev
gcloud artifacts repositories create prod-nba-images \
  --repository-format=docker --location=$GCP_REGION

docker build -f docker/Dockerfile.api \
  -t ${GCP_REGION}-docker.pkg.dev/${PROJECT_ID}/prod-nba-images/api:latest .
docker push ${GCP_REGION}-docker.pkg.dev/${PROJECT_ID}/prod-nba-images/api:latest

# 8. Train & upload initial model
python code/train_model.py
gsutil mb -l $GCP_REGION gs://${PROJECT_ID}-prod-nba-models/
gsutil cp trained_models/model_best_lr*.joblib gs://${PROJECT_ID}-prod-nba-models/initial/
```

## 🔧 Terraform Deployment (Phase 2)

```bash
cd terraform/environments/prod

# Create tfvars
cat > prod.tfvars <<EOF
project_id = "$PROJECT_ID"
region     = "$GCP_REGION"
environment = "prod"

api_image           = "${GCP_REGION}-docker.pkg.dev/${PROJECT_ID}/prod-nba-images/api:latest"
prediction_image    = "${GCP_REGION}-docker.pkg.dev/${PROJECT_ID}/prod-nba-images/prediction:latest"
api_min_instances   = 1
api_max_instances   = 2

enable_monitoring   = true
notification_email  = "your-email@company.com"
EOF

# Deploy
terraform init
terraform plan -var-file="prod.tfvars" -out=tfplan
terraform apply tfplan

# Get outputs
terraform output -json > deployment-outputs.json
```

## 🗄️ Database Setup (Phase 3)

```bash
# Get instance name
DB_INSTANCE=$(terraform output -raw database_instance_name)

# Initialize schema
gcloud sql connect $DB_INSTANCE --user=nba_user < code/database/init.sql

# Verify
gcloud sql connect $DB_INSTANCE --user=nba_user << EOF
\dt
\q
EOF
```

## ✅ Verification (Phase 4)

```bash
# Get URLs
API_URL=$(terraform output -raw api_url)
PRED_URL=$(terraform output -raw prediction_url)

# Test API
curl -X GET "$API_URL/health" -v

# Test prediction
curl -X GET "$PRED_URL/health" -v

# Check storage
gsutil ls gs://${PROJECT_ID}-prod-nba-models/

# Check logs
gcloud logs read --service=prod-nba-api --limit=50
```

---

## 🏗️ File Structure

```
nba_mlops/
├── TERRAFORM_DEPLOYMENT_PLAN.md        ← Read First (Overview)
├── TERRAFORM_DEPLOYMENT_GUIDE.md       ← Follow Step-by-Step
├── TERRAFORM_DEPLOYMENT_SUMMARY.md     ← Quick Reference
├── MIGRATION_AWS_TO_GCP.md            ← Code Updates
└── terraform/
    ├── environments/prod/
    │   ├── main.tf                    ← Provider config
    │   ├── variables.tf               ← Input vars
    │   ├── services.tf                ← Module calls
    │   ├── outputs.tf                 ← Export values
    │   ├── prod.tfvars.example        ← Config template
    │   └── terraform-key.json         ← Service account key (⚠️ .gitignore)
    └── modules/
        ├── database/                  ← Cloud SQL
        ├── cloud-run/                 ← API services
        ├── storage/                   ← GCS buckets
        └── monitoring/                ← Dashboards & alerts
```

---

## 🎯 What Gets Created

| Resource | Description | Cost |
|----------|-------------|------|
| **Cloud SQL** | PostgreSQL database (HA) | ~$150-200/mo |
| **Cloud Run** | 2 API services (auto-scaling) | ~$50-100/mo |
| **Cloud Storage** | 5 buckets (models, data, logs) | ~$2-5/mo |
| **Artifact Registry** | Docker images | Free tier |
| **Monitoring** | Dashboards, alerts, logging | ~$10-20/mo |
| **Service Accounts** | IAM identities | Free |
| **Secrets Manager** | Password storage | ~$6/mo |

**Total: ~$220-330/month**

---

## 🔑 Key Configuration Values

### From GCP (Auto-Generated)
```
database_instance_name = "prod-nba-db"
api_url = "https://prod-nba-api-xxxxx.run.app"
prediction_url = "https://prod-nba-prediction-xxxxx.run.app"
models_bucket = "nba-mlops-prod-nba-models"
raw_data_bucket = "nba-mlops-prod-nba-raw-data"
processed_data_bucket = "nba-mlops-prod-nba-processed-data"
```

### Store in `.env` for Local Testing
```bash
GOOGLE_PROJECT_ID=$PROJECT_ID
GCP_REGION=$GCP_REGION
CLOUDSQL_INSTANCE="prod-nba-db:europe-west3:prod-nba-db"
GCS_MODELS_BUCKET="nba-mlops-prod-nba-models"
API_URL="https://prod-nba-api-xxxxx.run.app"
```

---

## 🚨 Important Notes

1. **Keep `terraform-key.json` secret!**
   ```bash
   echo "terraform-key.json" >> .gitignore
   ```

2. **Terraform state is sensitive!**
   ```bash
   # Use remote backend in production
   terraform init -backend-config="bucket=$PROJECT_ID-terraform-state"
   ```

3. **Database password stored in Secret Manager**
   ```bash
   gcloud secrets versions list db-password
   ```

4. **Cloud Run auto-scales between min/max instances**
   - Adjust in `prod.tfvars` for cost control
   - Scale down dev: `api_min_instances=0, api_max_instances=2`

---

## ⚡ Common Quick Edits

### Scale up for load
```hcl
# Edit prod.tfvars
api_max_instances = 5      # Was 2
db_instance_tier = "db-n1-standard-4"  # Was db-n1-standard-1

# Apply
terraform apply -var-file="prod.tfvars"
```

### Add monitoring email
```hcl
notification_email = "ops-team@company.com"
```

### Enable/disable alerts
```hcl
enable_monitoring = false
```

---

## 📞 Emergency Commands

### View all resources
```bash
gcloud compute instances list
gcloud sql instances list
gsutil ls
```

### Kill & restart Cloud Run service
```bash
gcloud run services delete prod-nba-api --region=$GCP_REGION
terraform apply -var-file="prod.tfvars"
```

### Check service account permissions
```bash
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:terraform-sa"
```

### Destroy everything (⚠️ WARNING)
```bash
terraform destroy -var-file="prod.tfvars"
# This will DELETE all GCP resources created by Terraform
```

---

## 📊 Effort Summary

| Phase | Task | Time |
|-------|------|------|
| Manual Setup | Create GCP project, APIs, service account, secrets | 60-90 min |
| Docker Build | Build and push images to Artifact Registry | 30 min |
| Initial Model | Train and upload first model | 30 min |
| Terraform Deploy | `terraform apply` to create all infra | 30 min |
| Database Init | Load schema and seed data | 20 min |
| Verification | Test APIs, storage, monitoring | 30 min |
| **TOTAL** | | **3-4 hours** |

---

## ✅ Deployment Checklist

- [ ] GCP project created
- [ ] APIs enabled (8 services)
- [ ] Service account created with terraform-key.json
- [ ] Secrets created in Secret Manager
- [ ] Docker images built and pushed
- [ ] Initial model trained and uploaded
- [ ] prod.tfvars created with correct values
- [ ] `terraform plan` reviewed
- [ ] `terraform apply` completed successfully
- [ ] Database schema initialized
- [ ] APIs respond to health checks
- [ ] Cloud Storage buckets accessible
- [ ] Monitoring dashboard visible

---

## 🚀 You're Ready!

Everything is set up for production deployment. Follow the phases in order:

1. **Phase 1:** Manual setup (90 min)
2. **Phase 2:** Terraform deploy (30 min)
3. **Phase 3:** Database init (20 min)
4. **Phase 4:** Verification (30 min)

**Total time to production: ~3-4 hours**

Good luck! 🎉
