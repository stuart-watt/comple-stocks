resource "google_bigquery_dataset" "stocks" {
  dataset_id  = "stocks"
  description = "Contains ASX data"
  location    = "US"
}

resource "google_bigquery_table" "prices_raw" {
  dataset_id = google_bigquery_dataset.stocks.dataset_id
  table_id   = "prices_raw"

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
      "type": "FLOAT",
      "mode": "NULLABLE",
      "description": "Open price"
    },
    {
      "name": "close",
      "type": "FLOAT",
      "mode": "NULLABLE",
      "description": "Close price"
    },
    {
      "name": "low",
      "type": "FLOAT",
      "mode": "NULLABLE",
      "description": "Low price"
    },
    {
      "name": "high",
      "type": "FLOAT",
      "mode": "NULLABLE",
      "description": "High price"
    },
    {
      "name": "volume",
      "type": "FLOAT",
      "mode": "NULLABLE",
      "description": "VOlume"
    },
    {
      "name": "dividends",
      "type": "FLOAT",
      "mode": "NULLABLE",
      "description": "Dividends"
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
      "type": "FLOAT",
      "mode": "NULLABLE",
      "description": "Market Cap"
    }
  ]
  EOF
}

