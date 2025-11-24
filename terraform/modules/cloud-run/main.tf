# Cloud Run Module for NBA MLOps API and Frontend

resource "google_cloud_run_service" "api" {
  name     = "${var.environment}-nba-api"
  location = var.region
  project  = var.project_id

  template {
    spec {
      service_account_name = google_service_account.cloud_run.email

      containers {
        image = var.api_image
        
        ports {
          container_port = 8000
        }

        resources {
          limits = {
            cpu    = "1"
            memory = "1Gi"
          }
        }

        startup_probe {
          tcp_socket {
            port = 8000
          }
          initial_delay_seconds = 60
          timeout_seconds       = 5
          period_seconds        = 30
          failure_threshold     = 240
        }

        env {
          name  = "DB_HOST"
          value = var.db_host
        }

        env {
          name  = "DB_PORT"
          value = "5432"
        }

        env {
          name  = "DB_NAME"
          value = var.db_name
        }

        env {
          name  = "DB_USER"
          value = var.db_user
        }

        env {
          name  = "DB_PASSWORD"
          value_from {
            secret_key_ref {
              name = var.db_password_secret
              key  = "latest"
            }
          }
        }

        env {
          name  = "MODELS_BUCKET"
          value = var.models_bucket
        }

        env {
          name  = "ENV"
          value = var.environment
        }
      }
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale" = tostring(var.max_instances)
        "autoscaling.knative.dev/minScale" = tostring(var.min_instances)
        "run.googleapis.com/vpc-access-connector" = var.vpc_connector
        "run.googleapis.com/vpc-access-egress" = "all"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  depends_on = [
    google_service_account.cloud_run,
  ]
}

resource "google_cloud_run_service" "frontend" {
  name     = "${var.environment}-nba-frontend"
  location = var.region
  project  = var.project_id

  template {
    spec {
      service_account_name = google_service_account.cloud_run.email

      containers {
        image = var.frontend_image

        ports {
          container_port = 3000
        }

        resources {
          limits = {
            cpu    = "0.5"
            memory = "512Mi"
          }
        }

        startup_probe {
          tcp_socket {
            port = 3000
          }
          initial_delay_seconds = 60
          timeout_seconds       = 5
          period_seconds        = 30
          failure_threshold     = 240
        }

        env {
          name  = "REACT_APP_API_URL"
          value = var.api_url
        }

        env {
          name  = "ENV"
          value = var.environment
        }
      }
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale" = tostring(var.max_instances)
        "autoscaling.knative.dev/minScale" = tostring(var.min_instances)
        "run.googleapis.com/vpc-access-connector" = var.vpc_connector
        "run.googleapis.com/vpc-access-egress" = "all"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  depends_on = [
    google_service_account.cloud_run,
  ]
}

resource "google_cloud_run_service" "prediction" {
  name     = "${var.environment}-nba-prediction"
  location = var.region
  project  = var.project_id

  template {
    spec {
      service_account_name = google_service_account.cloud_run.email

      containers {
        image = var.prediction_image

        ports {
          container_port = 8001
        }

        resources {
          limits = {
            cpu    = "1"
            memory = "512Mi"
          }
        }

        startup_probe {
          tcp_socket {
            port = 8001
          }
          initial_delay_seconds = 60
          timeout_seconds       = 5
          period_seconds        = 30
          failure_threshold     = 240
        }

        env {
          name  = "DB_HOST"
          value = var.db_host
        }

        env {
          name  = "DB_PORT"
          value = "5432"
        }

        env {
          name  = "DB_NAME"
          value = var.db_name
        }

        env {
          name  = "MODELS_BUCKET"
          value = var.models_bucket
        }

        env {
          name  = "ENV"
          value = var.environment
        }
      }
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale" = tostring(var.max_instances)
        "autoscaling.knative.dev/minScale" = tostring(var.min_instances)
        "run.googleapis.com/vpc-access-connector" = var.vpc_connector
        "run.googleapis.com/vpc-access-egress" = "all"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  depends_on = [
    google_service_account.cloud_run,
  ]
}

# Service account for Cloud Run
resource "google_service_account" "cloud_run" {
  account_id   = "${var.environment}-nba-cloud-run"
  display_name = "NBA MLOps Cloud Run Service Account"
  project      = var.project_id
}

# IAM roles for Cloud Run service account
resource "google_project_iam_member" "cloud_run_cloudsql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.cloud_run.email}"
}

resource "google_project_iam_member" "cloud_run_storage_object_viewer" {
  project = var.project_id
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.cloud_run.email}"
}

resource "google_project_iam_member" "cloud_run_secretmanager_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.cloud_run.email}"
}

# Allow public access to API
resource "google_cloud_run_service_iam_member" "api_public" {
  service  = google_cloud_run_service.api.name
  location = google_cloud_run_service.api.location
  role     = "roles/run.invoker"
  member   = "allUsers"
  project  = var.project_id
}

# Allow public access to frontend
resource "google_cloud_run_service_iam_member" "frontend_public" {
  service  = google_cloud_run_service.frontend.name
  location = google_cloud_run_service.frontend.location
  role     = "roles/run.invoker"
  member   = "allUsers"
  project  = var.project_id
}

# Allow public access to prediction service
resource "google_cloud_run_service_iam_member" "prediction_public" {
  service  = google_cloud_run_service.prediction.name
  location = google_cloud_run_service.prediction.location
  role     = "roles/run.invoker"
  member   = "allUsers"
  project  = var.project_id
}
