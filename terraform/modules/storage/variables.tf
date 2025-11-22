variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "europe-west3"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "create_terraform_state_bucket" {
  description = "Whether to create a Terraform state bucket"
  type        = bool
  default     = true
}

variable "pipeline_service_account" {
  description = "Service account email for ML pipeline (Composer/Cloud Run)"
  type        = string
  default     = ""
}
