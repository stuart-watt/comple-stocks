WITH

  timestamp_master AS (
    SELECT
      `timestamp`
    FROM
      {{ ref("timestamp_master")}}
  ),

  prices AS (
    SELECT
      symbol,
      `timestamp`,
      `close` as price
    FROM
      {{ source("stocks", "prices_hourly")}}
  ),

  stock_master AS (
    SELECT
      `timestamp`,
      symbol
    FROM
      timestamp_master,
      (SELECT DISTINCT symbol FROM prices)
  )

SELECT
  symbol,
  `timestamp`,
  LAST_VALUE(price IGNORE NULLS) OVER (
    PARTITION BY symbol 
    ORDER BY `timestamp`
  ) AS price
FROM
  stock_master
LEFT JOIN
  prices 
USING (symbol, `timestamp`)
