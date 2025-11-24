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

variable "subnet_cidr" {
  description = "CIDR range for the subnet"
  type        = string
  default     = "10.0.1.0/24"
}

variable "connector_cidr" {
  description = "CIDR range for VPC Access Connector"
  type        = string
  default     = "10.8.0.0/28"
}

variable "connector_min_throughput" {
  description = "Minimum throughput for VPC Access Connector"
  type        = number
  default     = 200
}

variable "connector_max_throughput" {
  description = "Maximum throughput for VPC Access Connector"
  type        = number
  default     = 300
}
