resource "google_storage_bucket" "artifacts" {
  name = "${var.project_name}-artifacts"
  location = "US"
}

resource "google_storage_bucket" "datalake" {
  name = "${var.project_name}-datalake"
  location = "US"
}
