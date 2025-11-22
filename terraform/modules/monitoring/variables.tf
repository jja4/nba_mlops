variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "enable_notifications" {
  description = "Enable email notifications for alerts"
  type        = bool
  default     = true
}

variable "notification_email" {
  description = "Email address for alert notifications"
  type        = string
  default     = ""
}

variable "create_alert_policies" {
  description = "Create alert policies"
  type        = bool
  default     = true
}

variable "create_dashboards" {
  description = "Create monitoring dashboards"
  type        = bool
  default     = true
}

variable "create_log_sink" {
  description = "Create log sink for Cloud Storage"
  type        = bool
  default     = true
}

variable "logs_bucket_name" {
  description = "Cloud Storage bucket for logs"
  type        = string
}
