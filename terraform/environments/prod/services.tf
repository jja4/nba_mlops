# Enable required Google Cloud APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "compute.googleapis.com",
    "iam.googleapis.com",
    "run.googleapis.com",
    "sqladmin.googleapis.com",
    "storage.googleapis.com",
    "artifactregistry.googleapis.com",
    "secretmanager.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com",
    "servicenetworking.googleapis.com",
    "vpcaccess.googleapis.com",
  ])

  service            = each.value
  disable_on_destroy = false
}

# ===== NETWORKING =====
module "networking" {
  source = "../../modules/networking"

  project_id   = var.project_id
  region       = var.region
  environment  = var.environment
  subnet_cidr  = var.subnet_cidr
  connector_cidr = var.connector_cidr

  depends_on = [google_project_service.required_apis]
}

# ===== DATABASE =====
module "database" {
  source = "../../modules/database"

  project_id            = var.project_id
  region                = var.region
  environment           = var.environment
  instance_tier         = var.db_instance_tier
  availability_type     = var.db_availability_type
  backup_retention_days = 30
  private_network       = module.networking.vpc_network_id

  depends_on = [
    google_project_service.required_apis,
    module.networking,
  ]
}

# ===== DB INITIALIZATION JOB =====
module "db_init" {
  source = "../../modules/db-init"

  project_id                 = var.project_id
  region                     = var.region
  environment                = var.environment
  db_init_image              = var.db_init_image
  instance_name              = module.database.instance_name
  db_host                    = module.database.private_ip_address
  db_name                    = module.database.database_name
  db_user                    = module.database.database_user
  db_password                = module.database.database_password
  db_password_secret         = module.database.password_secret_id
  vpc_connector              = module.networking.vpc_connector_name

  depends_on = [
    module.database,
    module.networking,
    google_artifact_registry_repository.nba_images
  ]
}

# ===== STORAGE =====
module "storage" {
  source = "../../modules/storage"

  project_id      = var.project_id
  region          = var.region
  environment     = var.environment

  depends_on = [google_project_service.required_apis]
}

# ===== CLOUD RUN =====
module "cloud_run" {
  source = "../../modules/cloud-run"

  project_id                  = var.project_id
  region                      = var.region
  environment                 = var.environment
  api_image                   = var.api_image
  frontend_image              = var.frontend_image
  prediction_image            = var.prediction_image
  db_host                     = module.database.private_ip_address
  db_name                     = module.database.database_name
  db_user                     = module.database.database_user
  db_password_secret          = module.database.password_secret_id
  cloudsql_connection_name    = module.database.instance_connection_name
  vpc_connector               = module.networking.vpc_connector_name
  models_bucket               = module.storage.models_bucket
  min_instances               = var.api_min_instances
  max_instances               = var.api_max_instances
  api_url                     = "https://${var.environment}-nba-api-xxxxx.a.run.app"  # Will be updated after first deploy

  depends_on = [
    google_project_service.required_apis,
    module.database,
    module.storage,
    module.networking,
    module.db_init,
  ]
}

# ===== MONITORING =====
module "monitoring" {
  source = "../../modules/monitoring"

  count = var.enable_monitoring ? 1 : 0

  project_id          = var.project_id
  environment         = var.environment
  enable_notifications = var.notification_email != ""
  notification_email  = var.notification_email
  create_alert_policies = true
  create_dashboards   = true
  create_log_sink     = true
  logs_bucket_name    = module.storage.logs_bucket

  depends_on = [
    google_project_service.required_apis,
    module.storage,
  ]
}

# ===== ARTIFACT REGISTRY =====
resource "google_artifact_registry_repository" "nba_images" {
  location      = var.region
  repository_id = "${var.environment}-nba-images"
  description   = "Docker images for NBA MLOps"
  format        = "DOCKER"
  project       = var.project_id

  depends_on = [google_project_service.required_apis]
}
