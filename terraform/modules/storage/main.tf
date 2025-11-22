# Cloud Storage Module for models and logs

resource "google_storage_bucket" "models" {
  name          = "${var.project_id}-${var.environment}-nba-models"
  location      = var.region
  force_destroy = var.environment != "prod"

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  # Keep all model versions for rollback capability
  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      num_newer_versions = 20
    }
  }
}

resource "google_storage_bucket" "logs" {
  name          = "${var.project_id}-${var.environment}-nba-logs"
  location      = var.region
  force_destroy = var.environment != "prod"

  uniform_bucket_level_access = true

  # Automatically delete old logs
  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }
}

# Storage bucket for Terraform state (best practice)
resource "google_storage_bucket" "terraform_state" {
  count         = var.create_terraform_state_bucket ? 1 : 0
  name          = "${var.project_id}-terraform-state"
  location      = var.region
  force_destroy = false

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle {
    prevent_destroy = true
  }
}
