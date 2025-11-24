# Service account for the job
resource "google_service_account" "db_init" {
  account_id   = "${var.environment}-nba-db-init"
  display_name = "DB Init Service Account"
  project      = var.project_id
}

# Grant Cloud SQL client permission
resource "google_project_iam_member" "db_init_cloudsql" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.db_init.email}"
}

# Grant logging permission
resource "google_project_iam_member" "db_init_logging" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.db_init.email}"
}

# Grant Secret Manager Accessor permission
resource "google_project_iam_member" "db_init_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.db_init.email}"
}

# Cloud Run Job for Database Initialization
resource "google_cloud_run_v2_job" "db_init" {
  name     = "${var.environment}-db-init-job"
  location = var.region
  project  = var.project_id

  template {
    template {
      containers {
        image = var.db_init_image
        
        env {
          name  = "DB_HOST"
          value = var.db_host
        }
        env {
          name  = "DB_USER"
          value = var.db_user
        }
        env {
          name  = "DB_NAME"
          value = var.db_name
        }
        env {
          name = "DB_PASSWORD"
          value_source {
            secret_key_ref {
              secret  = var.db_password_secret
              version = "latest"
            }
          }
        }
      }
      
      vpc_access {
        connector = "projects/${var.project_id}/locations/${var.region}/connectors/${var.vpc_connector}"
        egress    = "ALL_TRAFFIC"
      }
      
      service_account = google_service_account.db_init.email
    }
  }

  depends_on = [
    google_project_iam_member.db_init_cloudsql,
    google_project_iam_member.db_init_logging,
    google_project_iam_member.db_init_secret_accessor
  ]
}

# Trigger the job immediately after creation
resource "null_resource" "db_init_trigger" {
  depends_on = [google_cloud_run_v2_job.db_init]

  provisioner "local-exec" {
    command = <<EOT
      echo "Triggering Cloud Run Job: ${google_cloud_run_v2_job.db_init.name}..."
      gcloud run jobs execute ${google_cloud_run_v2_job.db_init.name} \
        --region ${var.region} \
        --project ${var.project_id} \
        --wait
      
      if [ $? -eq 0 ]; then
        echo "✓ Database initialization job completed successfully!"
      else
        echo "✗ Database initialization job failed."
        exit 1
      fi
    EOT
  }
}
