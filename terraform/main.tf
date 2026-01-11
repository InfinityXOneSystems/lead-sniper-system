
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "4.51.0"
    }
    random = {
      source = "hashicorp/random"
      version = "3.1.0"
    }
  }
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

resource "random_id" "bucket_suffix" {
  byte_length = 4
}

resource "google_storage_bucket" "lead_sniper_bucket" {
  name          = "lead-sniper-bucket-${random_id.bucket_suffix.hex}"
  location      = var.gcp_region
  force_destroy = true
  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 7
    }
  }
}

resource "google_project_service" "firestore" {
  service = "firestore.googleapis.com"
}

resource "google_firestore_database" "database" {
  project     = var.gcp_project_id
  name        = "(default)"
  location_id = var.gcp_region
  type        = "FIRESTORE_NATIVE"

  depends_on = [google_project_service.firestore]
}

resource "google_bigquery_dataset" "lead_sniper_dataset" {
  dataset_id                  = "lead_sniper_dataset"
  friendly_name               = "Lead Sniper Dataset"
  description                 = "This dataset holds lead information for the Lead Sniper system."
  location                    = var.gcp_region
  delete_contents_on_destroy = true
}

resource "google_bigquery_table" "leads_table" {
  dataset_id = google_bigquery_dataset.lead_sniper_dataset.dataset_id
  table_id   = "leads"
  deletion_protection = false

  time_partitioning {
    type  = "DAY"
    field = "timestamp"
  }

  schema = <<EOF
[
  {
    "name": "id",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "The unique identifier for the lead."
  },
  {
    "name": "timestamp",
    "type": "TIMESTAMP",
    "mode": "REQUIRED",
    "description": "The time the lead was generated."
  },
  {
    "name": "source",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "The source of the lead."
  },
  {
    "name": "status",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "The status of the lead."
  }
]
EOF
}

resource "google_project_service" "vertex_ai" {
  service = "aiplatform.googleapis.com"
}

resource "google_vertex_ai_dataset" "lead_sniper_vertex_dataset" {
  display_name        = "lead_sniper_dataset"
  metadata_schema_uri = "gs://google-cloud-aiplatform/schema/dataset/metadata/tabular_1.0.0.yaml"
  project             = var.gcp_project_id
  region              = var.gcp_region
  depends_on          = [google_project_service.vertex_ai]
}

resource "google_vertex_ai_featurestore" "lead_sniper_featurestore" {
  name     = "lead_sniper_featurestore"
  project  = var.gcp_project_id
  region   = var.gcp_region
  online_serving_config {
    fixed_node_count = 1
  }
  depends_on = [google_project_service.vertex_ai]
}

resource "google_vertex_ai_endpoint" "lead_sniper_endpoint" {
  name         = "lead_sniper_endpoint"
  display_name = "Lead Sniper Endpoint"
  project      = var.gcp_project_id
  region       = var.gcp_region
  depends_on   = [google_project_service.vertex_ai]
}
resource "google_project_service" "run" {
  service = "run.googleapis.com"
}

resource "google_service_account" "lead_sniper_sa" {
  account_id   = "lead-sniper-sa"
  display_name = "Lead Sniper Service Account"
}

resource "google_cloud_run_v2_service" "lead_sniper_service" {
  name     = "lead-sniper-service"
  location = var.gcp_region
  project  = var.gcp_project_id

  template {
    service_account = google_service_account.lead_sniper_sa.email
    containers {
      image = "us-docker.pkg.dev/cloudrun/container/hello"
    }
  }

  depends_on = [google_project_service.run]
}

resource "google_cloud_run_service_iam_member" "noauth" {
  location = google_cloud_run_v2_service.lead_sniper_service.location
  service  = google_cloud_run_v2_service.lead_sniper_service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
