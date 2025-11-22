# GCP Setup & Terraform Deployment Guide

## 🚀 Part 1: Manual GCP Setup (One-Time)

### 1.1 Create GCP Account & Project

```bash
# If you don't have a GCP account:
# Go to https://cloud.google.com
# Sign up with Google account
# Enable billing

# Option 1: Using Homebrew (easiest)
brew install google-cloud-sdk

# Option 2: Manual download
# Go to: https://cloud.google.com/sdk/docs/install
# Download macOS installer and follow steps

# Verify installation
gcloud --version
# Should output: Google Cloud SDK x.x.x

# Authenticate Your Account
# This opens a browser to log in
gcloud auth login

# Follow the prompts:
# 1. Browser opens → Google login page
# 2. Sign in with your Google account
# 3. Grant permissions to gcloud
# 4. Returns to terminal authenticated

# Once logged in, create a project:
gcloud projects create nba-mlops-prod --name="NBA MLOps"
gcloud config set project nba-mlops-prod

# Get your project ID
PROJECT_ID=$(gcloud config get-value project)
echo "Project ID: $PROJECT_ID"

# Enable Billing on the new Project
gcloud billing accounts list
BILLING_ACCOUNT_ID=$(gcloud billing accounts list --format="value(ACCOUNT_ID)" --limit=1)
echo "Billing Account ID: $BILLING_ACCOUNT_ID"

gcloud billing projects link $PROJECT_ID --billing-account=$BILLING_ACCOUNT_ID
```

### 1.2 Enable Required APIs

```bash
# Enable all necessary services
gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  storage.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  monitoring.googleapis.com \
  logging.googleapis.com \
  cloudresourcemanager.googleapis.com

# Verify they're enabled
gcloud services list --enabled | grep -E "run|sql|storage|artifact|secret"
```

### 1.3 Create Service Account for Terraform

```bash
PROJECT_ID=$(gcloud config get-value project)

# Create service account
gcloud iam service-accounts create terraform-sa \
  --display-name="Terraform Service Account"

# Grant necessary permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:terraform-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/viewer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:terraform-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:terraform-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:terraform-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/cloudsql.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:terraform-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/compute.networkUser"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:terraform-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:terraform-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:terraform-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/secretmanager.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:terraform-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/monitoring.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:terraform-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/logging.admin"


# Create and download key
gcloud iam service-accounts keys create terraform-key.json \
  --iam-account=terraform-sa@${PROJECT_ID}.iam.gserviceaccount.com

# Set authentication
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/terraform-key.json"
```

**⚠️ CRITICAL:** This `terraform-key.json` file grants full access. **NEVER commit to git!**


### 1.4 Create Docker Registry & Push Images

```bash
PROJECT_ID=$(gcloud config get-value project)

# Create Artifact Registry
gcloud artifacts repositories create prod-nba-images \
  --repository-format=docker \
  --location=europe-west3 \
  --description="NBA MLOps Docker Images"

# Configure Docker authentication
gcloud auth configure-docker europe-west3-docker.pkg.dev

# Build and push API image
docker build -f docker/Dockerfile.api \
  -t europe-west3-docker.pkg.dev/${PROJECT_ID}/prod-nba-images/api:latest .
docker push europe-west3-docker.pkg.dev/${PROJECT_ID}/prod-nba-images/api:latest

# Build and push Frontend image
docker build -f docker/Dockerfile.react \
  -t europe-west3-docker.pkg.dev/${PROJECT_ID}/prod-nba-images/frontend:latest .
docker push europe-west3-docker.pkg.dev/${PROJECT_ID}/prod-nba-images/frontend:latest

# Build and push Prediction image
docker build -f docker/Dockerfile.prediction-service \
  -t europe-west3-docker.pkg.dev/${PROJECT_ID}/prod-nba-images/prediction:latest .
docker push europe-west3-docker.pkg.dev/${PROJECT_ID}/prod-nba-images/prediction:latest

# Verify
gcloud artifacts docker images list europe-west3-docker.pkg.dev/${PROJECT_ID}/prod-nba-images
```

---

## 🔧 Part 2: Configure Terraform

### 2.1 Create prod.tfvars (Local Only - NEVER Git!)

```bash
cd terraform/environments/prod

# Copy template
cp prod.tfvars.example prod.tfvars

# Edit prod.tfvars with YOUR values
cat > prod.tfvars <<EOF
project_id         = "YOUR-GCP-PROJECT-ID"
region              = "europe-west3"
environment         = "prod"

db_instance_tier    = "db-f1-micro"
db_availability_type = "ZONAL"

api_image           = "europe-west3-docker.pkg.dev/YOUR-GCP-PROJECT-ID/prod-nba-images/api:latest"
frontend_image      = "europe-west3-docker.pkg.dev/YOUR-GCP-PROJECT-ID/prod-nba-images/frontend:latest"
prediction_image    = "europe-west3-docker.pkg.dev/YOUR-GCP-PROJECT-ID/prod-nba-images/prediction:latest"

api_min_instances   = 1
api_max_instances   = 2

enable_monitoring   = true
notification_email  = "your-email@company.com"
EOF

# Verify it looks right (contains YOUR actual project ID)
cat prod.tfvars
```

### 2.2 Set Terraform Environment Variable

```bash
# Set authentication for Terraform
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/terraform-key.json"

# Verify it works
gcloud auth list
```

### 2.3 Initialize Terraform

```bash
cd terraform/environments/prod

# Initialize (downloads provider plugins)
terraform init

# You should see "Terraform has been successfully configured!"
```

---

## 🔐 Part 3: Keep Secrets Safe

### 3.1 Git Ignore Sensitive Files

```bash
# Create/update .gitignore in project root
cat >> .gitignore <<'EOF'
# Terraform sensitive files
terraform-key.json
terraform-key-*.json
*.tfvars
!*.tfvars.example
.terraform/
.terraform.lock.hcl
crash.log

# Environment variables
.env
.env.local
.env.*.local

# IDE
.idea/
.vscode/
*.swp
*.swo
EOF

# Verify sensitive files aren't tracked
git status | grep terraform-key  # Should show nothing
git status | grep "*.tfvars"     # Should show nothing
```

### 3.2 Where to Store Secrets

**Option A: Local Environment Variables (Recommended for Development)**
```bash
# Don't commit these - keep locally only
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/terraform-key.json"
export TF_VAR_notification_email="your-email@company.com"

# Use in Terraform
terraform apply -var-file="prod.tfvars"
```

**Option B: Secret Management (Recommended for Team/CI)**

For production/CI pipelines, use Google Secret Manager:

```bash
# Store service account key in Secret Manager
cat terraform-key.json | gcloud secrets create terraform-key --data-file=-

# Store other secrets
echo "your-notification-email@company.com" | gcloud secrets create notification-email --data-file=-

# Retrieve in CI/CD pipeline
GOOGLE_APPLICATION_CREDENTIALS=$(gcloud secrets versions access latest --secret="terraform-key" > /tmp/key.json)
export GOOGLE_APPLICATION_CREDENTIALS="/tmp/key.json"
```

### 3.3 Database Password

The database password is auto-generated and stored in Google Secret Manager:

```bash
# Terraform automatically creates it
# View it (stored safely in GCP):
gcloud secrets versions access latest --secret="prod-nba-db-password"
```

---

## ✅ Code Changes You Need to Make

### Update prod.tfvars.example (Already Done)

The example file shows placeholders. When you deploy:

```hcl
# BEFORE (example):
project_id = "YOUR-GCP-PROJECT-ID"
api_image = "europe-west3-docker.pkg.dev/YOUR-PROJECT-ID/prod-nba-images/api:latest"

# AFTER (your prod.tfvars):
project_id = "nba-mlops-prod"  # Your actual project ID
api_image = "europe-west3-docker.pkg.dev/nba-mlops-prod/prod-nba-images/api:latest"
```

### No Code Changes Needed

- ✅ `main.tf` - Uses `var.project_id` dynamically
- ✅ `variables.tf` - Reads from prod.tfvars
- ✅ `services.tf` - Uses Artifact Registry from tfvars
- ✅ Cloud Run - Connects to Cloud SQL dynamically

---

## 🚀 Deploy Checklist

```bash
# 1. Authenticate
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/terraform-key.json"

# 2. Plan (review changes)
cd terraform/environments/prod
terraform plan -var-file="prod.tfvars"

# 3. Apply (create resources)
terraform apply -var-file="prod.tfvars"

# 4. Get outputs
terraform output

# 5. Test
API_URL=$(terraform output -raw api_url)
curl "$API_URL/health"
```

---

## 🛡️ Security Best Practices

### ✅ DO:
- ✅ Keep `terraform-key.json` only locally
- ✅ Add to `.gitignore` (already done)
- ✅ Use service account (not personal account)
- ✅ Restrict service account permissions (use roles/editor, not roles/owner)
- ✅ Rotate keys periodically
- ✅ Use Secret Manager for production

### ❌ DON'T:
- ❌ Commit `prod.tfvars` to git
- ❌ Commit `terraform-key.json` to git
- ❌ Share service account key in chat/email
- ❌ Use `gcloud auth login` for Terraform (use service account)
- ❌ Hardcode secrets in code

---

## 🔄 Workflow Summary

```
1. Manual Setup (One-time)
   - Create GCP project
   - Enable APIs
   - Create service account + key
   - Build & push Docker images

2. Code Configuration (One-time)
   - Copy prod.tfvars.example → prod.tfvars
   - Edit with your actual values
   - Add to .gitignore

3. Deploy (Repeatable)
   - Set GOOGLE_APPLICATION_CREDENTIALS
   - terraform plan
   - terraform apply

4. Redeploy (When code changes)
   - Rebuild Docker images
   - Push to Artifact Registry
   - Increment image tag in prod.tfvars
   - terraform apply
```

---

## 📋 What's Automated vs Manual

| Task | Who | How |
|------|-----|-----|
| Create GCP project | You | `gcloud projects create` |
| Enable APIs | You | `gcloud services enable` |
| Create service account | You | `gcloud iam service-accounts create` |
| Build Docker images | You | `docker build & push` |
| Create database | Terraform | `terraform apply` |
| Create Cloud Run services | Terraform | `terraform apply` |
| Create storage buckets | Terraform | `terraform apply` |
| Manage backups | GCP (automatic) | Cloud SQL handles it |

---

## 🆘 Troubleshooting

**Error: "Permission denied"**
```bash
# Verify service account is set
echo $GOOGLE_APPLICATION_CREDENTIALS

# Verify key is valid
gcloud auth list

# Re-authenticate
gcloud auth activate-service-account --key-file=terraform-key.json
```

**Error: "Project not found"**
```bash
# Check project ID is correct
gcloud config get-value project

# List available projects
gcloud projects list
```

**Error: "Image not found"**
```bash
# Verify images were pushed
gcloud artifacts docker images list europe-west3-docker.pkg.dev/YOUR-PROJECT-ID/prod-nba-images

# Rebuild and push if needed
docker build -f docker/Dockerfile.api -t europe-west3-docker.pkg.dev/YOUR-PROJECT-ID/prod-nba-images/api:latest .
docker push europe-west3-docker.pkg.dev/YOUR-PROJECT-ID/prod-nba-images/api:latest
```

---

**Next Step:** Follow the checklist above and run `terraform plan` to verify everything works! 🚀
