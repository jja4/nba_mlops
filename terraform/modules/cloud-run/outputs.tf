output "api_service_name" {
  description = "Cloud Run API service name"
  value       = google_cloud_run_service.api.name
}

output "api_url" {
  description = "Cloud Run API service URL"
  value       = google_cloud_run_service.api.status[0].url
}

output "frontend_service_name" {
  description = "Cloud Run Frontend service name"
  value       = google_cloud_run_service.frontend.name
}

output "frontend_url" {
  description = "Cloud Run Frontend service URL"
  value       = google_cloud_run_service.frontend.status[0].url
}

output "prediction_service_name" {
  description = "Cloud Run Prediction service name"
  value       = google_cloud_run_service.prediction.name
}

output "prediction_url" {
  description = "Cloud Run Prediction service URL"
  value       = google_cloud_run_service.prediction.status[0].url
}

output "service_account_email" {
  description = "Service account email for Cloud Run"
  value       = google_service_account.cloud_run.email
}
