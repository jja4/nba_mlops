output "notification_channel_id" {
  description = "Monitoring notification channel ID"
  value       = try(google_monitoring_notification_channel.email[0].id, null)
}

output "alert_policy_ids" {
  description = "Alert policy IDs"
  value = {
    cloud_run_errors = try(google_monitoring_alert_policy.cloud_run_errors[0].id, null)
    cloud_sql_cpu    = try(google_monitoring_alert_policy.cloud_sql_cpu[0].id, null)
    cloud_sql_disk   = try(google_monitoring_alert_policy.cloud_sql_disk[0].id, null)
  }
}

output "dashboard_id" {
  description = "Monitoring dashboard ID"
  value       = try(google_monitoring_dashboard.nba_mlops[0].id, null)
}

output "log_sink_name" {
  description = "Log sink name"
  value       = try(google_logging_project_sink.nba_logs[0].name, null)
}
