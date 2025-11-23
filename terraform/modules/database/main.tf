# Cloud SQL Database Module

resource "google_sql_database_instance" "postgres" {
  name                = "${var.environment}-nba-db"
  database_version    = "POSTGRES_15"
  region              = var.region
  deletion_protection = var.environment == "prod" ? true : false

  settings {
    tier              = var.instance_tier
    availability_type = var.availability_type

    # Backup configuration
    backup_configuration {
      enabled                        = true
      point_in_time_recovery_enabled = true
      location                       = var.region
    }

    # IP configuration
    ip_configuration {
      ipv4_enabled    = true
      private_network = var.private_network
      require_ssl     = true
      authorized_networks {
        name  = "allow-all"
        value = "0.0.0.0/0"
      }
    }

    # Maintenance window
    maintenance_window {
      day          = 7  # Sunday
      hour         = 3
      update_track = "stable"
    }

    # Database flags for performance
    database_flags {
      name  = "max_connections"
      value = "100"
    }

    database_flags {
      name  = "shared_buffers"
      value = "262144"  # 2GB
    }
  }

  depends_on = [var.module_depends_on]
}

resource "google_sql_database" "nba_db" {
  name     = var.database_name
  instance = google_sql_database_instance.postgres.name
  charset  = "UTF8"
}

resource "random_password" "db_password" {
  length      = 32
  special     = true
  min_special = 2
  override_special = "!@#$%-_=+"
}

resource "google_sql_user" "nba_user" {
  name     = var.database_user
  instance = google_sql_database_instance.postgres.name
  password = random_password.db_password.result
}

# Store password in Secret Manager
resource "google_secret_manager_secret" "db_password_secret" {
  secret_id = "${var.environment}-nba-db-password"

  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }
}

resource "google_secret_manager_secret_version" "db_password_version" {
  secret      = google_secret_manager_secret.db_password_secret.id
  secret_data = random_password.db_password.result
}

# Backup storage bucket
resource "google_storage_bucket" "db_backups" {
  name          = "${var.project_id}-${var.environment}-db-backups"
  location      = var.region
  force_destroy = var.environment != "prod"

  uniform_bucket_level_access = true

  lifecycle_rule {
    condition {
      age = var.backup_retention_days
    }
    action {
      type = "Delete"
    }
  }

  versioning {
    enabled = true
  }
}
