# Monitoring and Logging Module

resource "google_monitoring_notification_channel" "email" {
  count           = var.enable_notifications ? 1 : 0
  display_name    = "NBA MLOps Email Notifications"
  type            = "email"
  labels = {
    email_address = var.notification_email
  }
  enabled = true
}

# Alert policy for Cloud Run errors
resource "google_monitoring_alert_policy" "cloud_run_errors" {
  count           = var.create_alert_policies ? 1 : 0
  display_name    = "${var.environment}-nba-cloud-run-errors"
  combiner        = "OR"
  notification_channels = var.enable_notifications ? [google_monitoring_notification_channel.email[0].id] : []

  conditions {
    display_name = "High error rate"

    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"${var.environment}-nba-api\" AND metric.type=\"run.googleapis.com/request_count\" AND metric.labels.response_code_class=\"5xx\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 10

      aggregations {
        alignment_period  = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }
}

# Alert policy for Cloud SQL CPU
resource "google_monitoring_alert_policy" "cloud_sql_cpu" {
  count           = var.create_alert_policies ? 1 : 0
  display_name    = "${var.environment}-nba-cloudsql-cpu"
  combiner        = "OR"
  notification_channels = var.enable_notifications ? [google_monitoring_notification_channel.email[0].id] : []

  conditions {
    display_name = "High CPU usage"

    condition_threshold {
      filter          = "resource.type=\"cloudsql_database\" AND metric.type=\"cloudsql.googleapis.com/database/cpu/utilization\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0.8

      aggregations {
        alignment_period  = "60s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }
}

# Alert policy for Cloud SQL disk usage
resource "google_monitoring_alert_policy" "cloud_sql_disk" {
  count           = var.create_alert_policies ? 1 : 0
  display_name    = "${var.environment}-nba-cloudsql-disk"
  combiner        = "OR"
  notification_channels = var.enable_notifications ? [google_monitoring_notification_channel.email[0].id] : []

  conditions {
    display_name = "High disk usage"

    condition_threshold {
      filter          = "resource.type=\"cloudsql_database\" AND metric.type=\"cloudsql.googleapis.com/database/disk/utilization\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0.9

      aggregations {
        alignment_period  = "60s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }
}

# Custom monitoring dashboard
resource "google_monitoring_dashboard" "nba_mlops" {
  count           = var.create_dashboards ? 1 : 0
  dashboard_json  = jsonencode({
    displayName = "${var.environment}-nba-mlops-dashboard"
    mosaicLayout = {
      columns = 12
      tiles = [
        {
          width  = 6
          height = 4
          widget = {
            title = "Cloud Run Request Count"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"${var.environment}-nba-api\" AND metric.type=\"run.googleapis.com/request_count\""
                      aggregation = {
                        alignmentPeriod  = "60s"
                        perSeriesAligner = "ALIGN_RATE"
                      }
                    }
                  }
                }
              ]
            }
          }
        },
        {
          xPos   = 6
          width  = 6
          height = 4
          widget = {
            title = "Cloud SQL CPU Usage"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"cloudsql_database\" AND metric.type=\"cloudsql.googleapis.com/database/cpu/utilization\""
                      aggregation = {
                        alignmentPeriod  = "60s"
                        perSeriesAligner = "ALIGN_MEAN"
                      }
                    }
                  }
                }
              ]
            }
          }
        },
        {
          yPos   = 4
          width  = 6
          height = 4
          widget = {
            title = "Cloud SQL Disk Usage"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"cloudsql_database\" AND metric.type=\"cloudsql.googleapis.com/database/disk/utilization\""
                      aggregation = {
                        alignmentPeriod  = "60s"
                        perSeriesAligner = "ALIGN_MEAN"
                      }
                    }
                  }
                }
              ]
            }
          }
        },
        {
          xPos   = 6
          yPos   = 4
          width  = 6
          height = 4
          widget = {
            title = "Cloud Run Error Rate"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_count\" AND metric.labels.response_code_class=\"5xx\""
                      aggregation = {
                        alignmentPeriod  = "60s"
                        perSeriesAligner = "ALIGN_RATE"
                      }
                    }
                  }
                }
              ]
            }
          }
        }
      ]
    }
  })
}

# Log sink for application logs
resource "google_logging_project_sink" "nba_logs" {
  count       = var.create_log_sink ? 1 : 0
  name        = "${var.environment}-nba-logs-sink"
  destination = "storage.googleapis.com/${var.logs_bucket_name}"
  filter      = "resource.type=cloud_run_revision AND resource.labels.service_name=~\"${var.environment}-nba.*\""
  unique_writer_identity = true
}

resource "google_storage_bucket_iam_member" "log_sink" {
  count  = var.create_log_sink ? 1 : 0
  bucket = var.logs_bucket_name
  role   = "roles/storage.objectCreator"
  member = google_logging_project_sink.nba_logs[0].writer_identity
}
