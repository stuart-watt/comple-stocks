resource "google_bigquery_dataset" "stocks" {
  dataset_id  = "stocks"
  description = "Contains ASX data"
  location    = "US"
}

resource "google_bigquery_table" "prices" {
  dataset_id = google_bigquery_dataset.stocks.dataset_id
  table_id   = "prices"

  time_partitioning {
    type = "DAY"
  }

  schema = <<EOF
  [
    {
      "name": "symbol",
      "type": "STRING",
      "mode": "NULLABLE",
      "description": "ASX company ticker"
    },
    {
      "name": "timestamp",
      "type": "TIMESTAMP",
      "mode": "NULLABLE",
      "description": "Timestamp"
    },
    {
      "name": "open",
      "type": "NUMERIC",
      "mode": "NULLABLE",
      "description": "Open price"
    },
    {
      "name": "close",
      "type": "NUMERIC",
      "mode": "NULLABLE",
      "description": "Close price"
    },
    {
      "name": "low",
      "type": "NUMERIC",
      "mode": "NULLABLE",
      "description": "Low price"
    },
    {
      "name": "high",
      "type": "NUMERIC",
      "mode": "NULLABLE",
      "description": "High price"
    },
    {
      "name": "volume",
      "type": "NUMERIC",
      "mode": "NULLABLE",
      "description": "VOlume"
    }
  ]
  EOF
}

resource "google_bigquery_table" "listed_companies" {
  dataset_id = google_bigquery_dataset.stocks.dataset_id
  table_id   = "listed_companies"

  schema = <<EOF
  [
    {
      "name": "symbol",
      "type": "STRING",
      "mode": "NULLABLE",
      "description": "ASX company ticker"
    },
    {
      "name": "name",
      "type": "STRING",
      "mode": "NULLABLE",
      "description": "ASX company name"
    },
    {
      "name": "GIC",
      "type": "STRING",
      "mode": "NULLABLE",
      "description": "GICs industry group"
    },
    {
      "name": "listing_date",
      "type": "DATE",
      "mode": "NULLABLE",
      "description": "Date listed"
    },
    {
      "name": "market_cap",
      "type": "NUMERIC",
      "mode": "NULLABLE",
      "description": "Market Cap"
    }
  ]
  EOF
}

