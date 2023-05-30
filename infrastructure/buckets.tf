resource "google_storage_bucket" "artifacts" {
  name = "stock-prompter-artifacts"
  location = "US"
}

resource "google_storage_bucket" "datalake" {
  name = "stock-prompter-datalake"
  location = "US"
}
