output "raw_data_bucket" {
  description = "Raw data bucket name"
  value       = null
}

output "processed_data_bucket" {
  description = "Processed data bucket name"
  value       = null
}

output "models_bucket" {
  description = "Models bucket name"
  value       = google_storage_bucket.models.name
}

output "logs_bucket" {
  description = "Logs bucket name"
  value       = google_storage_bucket.logs.name
}

output "terraform_state_bucket" {
  description = "Terraform state bucket name"
  value       = try(google_storage_bucket.terraform_state[0].name, null)
}
