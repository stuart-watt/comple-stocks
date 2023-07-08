resource "google_pubsub_topic" "ingestor" {
  name = "stock-ingestion"
}

resource "google_pubsub_topic" "stock_notification" {
  name = "stock_notification"
}

resource "google_pubsub_topic" "trade_simulator" {
  name = "trade_simulator"
}

resource "google_pubsub_topic" "discord_poll" {
  name = "discord_poll"
}
