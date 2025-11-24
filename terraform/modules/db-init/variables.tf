variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "instance_name" {
  description = "Cloud SQL instance name"
  type        = string
}

variable "db_init_image" {
  description = "Docker image for DB initialization"
  type        = string
}

variable "db_host" {
  description = "Database host IP"
  type        = string
}

variable "db_user" {
  description = "Database user"
  type        = string
}

variable "db_name" {
  description = "Database name"
  type        = string
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "db_password_secret" {
  description = "Secret Manager secret ID for database password"
  type        = string
}

variable "vpc_connector" {
  description = "VPC Connector name for Cloud Run Job"
  type        = string
}
