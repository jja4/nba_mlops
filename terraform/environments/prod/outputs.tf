output "database_instance_name" {
  description = "Cloud SQL instance name"
  value       = module.database.instance_name
}

output "database_connection_name" {
  description = "Cloud SQL connection name"
  value       = module.database.instance_connection_name
}

output "api_url" {
  description = "Cloud Run API service URL"
  value       = module.cloud_run.api_url
}

output "frontend_url" {
  description = "Cloud Run frontend service URL"
  value       = module.cloud_run.frontend_url
}

output "prediction_url" {
  description = "Cloud Run prediction service URL"
  value       = module.cloud_run.prediction_url
}

output "models_bucket" {
  description = "Cloud Storage bucket for models"
  value       = module.storage.models_bucket
}

output "logs_bucket" {
  description = "Cloud Storage bucket for logs"
  value       = module.storage.logs_bucket
}

output "artifact_registry_repository" {
  description = "Artifact Registry repository name"
  value       = google_artifact_registry_repository.nba_images.name
}

output "cloud_run_service_account" {
  description = "Service account email for Cloud Run"
  value       = module.cloud_run.service_account_email
}
