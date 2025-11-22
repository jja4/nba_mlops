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

variable "api_image" {
  description = "Container image URL for API service"
  type        = string
}

variable "frontend_image" {
  description = "Container image URL for frontend service"
  type        = string
}

variable "prediction_image" {
  description = "Container image URL for prediction service"
  type        = string
}

variable "db_host" {
  description = "Database host"
  type        = string
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "nba_db"
}

variable "db_user" {
  description = "Database user"
  type        = string
  default     = "nba_user"
}

variable "db_password_secret" {
  description = "Secret Manager secret ID for database password"
  type        = string
}

variable "cloudsql_connection_name" {
  description = "Cloud SQL instance connection name"
  type        = string
}

variable "models_bucket" {
  description = "Cloud Storage bucket for models"
  type        = string
}

variable "min_instances" {
  description = "Minimum number of Cloud Run instances"
  type        = number
  default     = 1
}

variable "max_instances" {
  description = "Maximum number of Cloud Run instances"
  type        = number
  default     = 2
}

variable "api_url" {
  description = "API URL for frontend environment variable"
  type        = string
}
