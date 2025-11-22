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
  description = "Environment name"
  type        = string
  default     = "prod"
}

# Database variables
variable "db_instance_tier" {
  description = "Cloud SQL instance tier"
  type        = string
  default     = "db-n1-standard-1"
}

variable "db_availability_type" {
  description = "Database availability type"
  type        = string
  default     = "REGIONAL"
}

# Cloud Run variables
variable "api_image" {
  description = "Container image for API service"
  type        = string
}

variable "frontend_image" {
  description = "Container image for frontend service"
  type        = string
}

variable "prediction_image" {
  description = "Container image for prediction service"
  type        = string
}

variable "api_min_instances" {
  description = "Minimum number of API instances"
  type        = number
  default     = 1
}

variable "api_max_instances" {
  description = "Maximum number of API instances"
  type        = number
  default     = 2
}

# Monitoring variables
variable "enable_monitoring" {
  description = "Enable monitoring and alerts"
  type        = bool
  default     = true
}

variable "notification_email" {
  description = "Email for alert notifications"
  type        = string
  default     = ""
}
