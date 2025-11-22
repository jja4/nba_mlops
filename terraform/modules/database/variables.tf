variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "instance_tier" {
  description = "Cloud SQL instance tier"
  type        = string
  default     = "db-f1-micro"
}

variable "availability_type" {
  description = "Availability type (REGIONAL or ZONAL)"
  type        = string
  default     = "REGIONAL"
}

variable "database_name" {
  description = "Database name"
  type        = string
  default     = "nba_db"
}

variable "database_user" {
  description = "Database user"
  type        = string
  default     = "nba_user"
}

variable "backup_retention_days" {
  description = "Number of days to retain backups"
  type        = number
  default     = 30
}

variable "private_network" {
  description = "VPC network for private IP"
  type        = string
  default     = null
}

variable "depends_on" {
  description = "Resources to depend on"
  type        = list(any)
  default     = []
}
