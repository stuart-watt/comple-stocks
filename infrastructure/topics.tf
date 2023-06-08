resource "google_pubsub_topic" "ingestor" {
  name = "stock-ingestion"
}

resource "google_pubsub_topic" "stock_notification" {
  name = "stock_notification"
}
