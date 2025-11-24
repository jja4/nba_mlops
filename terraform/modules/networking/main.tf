# VPC Networking Module for NBA MLOps

# Create VPC Network
resource "google_compute_network" "vpc" {
  name                    = "${var.environment}-nba-vpc"
  auto_create_subnetworks = false
  project                 = var.project_id
}

# Create Subnet
resource "google_compute_subnetwork" "subnet" {
  name          = "${var.environment}-nba-subnet"
  ip_cidr_range = var.subnet_cidr
  region        = var.region
  network       = google_compute_network.vpc.id
  project       = var.project_id

  private_ip_google_access = true
}

# Create VPC Connector for Cloud Run
resource "google_vpc_access_connector" "connector" {
  name          = "${var.environment}-nba-connector"
  ip_cidr_range = var.connector_cidr
  network       = google_compute_network.vpc.name
  region        = var.region
  min_throughput = var.connector_min_throughput
  max_throughput = var.connector_max_throughput
  project       = var.project_id

  depends_on = [google_compute_subnetwork.subnet]
}

# Cloud SQL Private Service Connection
resource "google_compute_global_address" "private_ip_address" {
  name          = "${var.environment}-nba-db-private-ip"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.vpc.id
  project       = var.project_id
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.vpc.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_address.name]
}
