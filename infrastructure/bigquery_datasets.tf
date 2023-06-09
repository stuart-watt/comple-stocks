resource "google_bigquery_dataset" "stocks" {
  dataset_id  = "stocks"
  description = "Contains ASX data"
  location    = "US"
}
