
data "google_secret_manager_secret_version_access" "webhook" {
  secret = "stock-channel-webhook"
}
