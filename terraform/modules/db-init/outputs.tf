output "initialization_status" {
  description = "Status of database initialization"
  value       = "Database initialization completed"
  depends_on  = [null_resource.db_init_trigger]
}
