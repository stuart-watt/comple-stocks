resource "google_storage_bucket" "artifacts" {
  name = "stock-prompter-artifacts"
  location = "US"
}