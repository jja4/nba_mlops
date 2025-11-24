output "instance_name" {
  description = "Cloud SQL instance name"
  value       = google_sql_database_instance.postgres.name
}

output "instance_connection_name" {
  description = "Cloud SQL instance connection name"
  value       = google_sql_database_instance.postgres.connection_name
}

output "private_ip_address" {
  description = "Private IP address of the instance"
  value       = google_sql_database_instance.postgres.private_ip_address
  sensitive   = true
}

output "database_name" {
  description = "Database name"
  value       = google_sql_database.nba_db.name
}

output "database_user" {
  description = "Database user"
  value       = google_sql_user.nba_user.name
}

output "database_password" {
  description = "Database password (stored in Secret Manager)"
  value       = google_secret_manager_secret.db_password_secret.id
  sensitive   = true
}

output "password_secret_id" {
  description = "Secret Manager secret ID for database password"
  value       = google_secret_manager_secret.db_password_secret.secret_id
}

output "db_backups_bucket" {
  description = "Cloud Storage bucket for database backups"
  value       = google_storage_bucket.db_backups.name
}
