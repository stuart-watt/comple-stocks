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
      (SELECT DISTINCT symbol FROM prices UNION ALL SELECT "$AUD" as symbol) -- adds symbol for AUD
  ),

  new_prices AS (
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
      (SELECT * FROM prices_numbered WHERE rn = 1)
    USING (symbol, `timestamp`)
  )

SELECT 
  symbol,
  `timestamp`,
  COALESCE(price, 1) as price
FROM 
  new_prices 
{% if is_incremental() %}
  WHERE
    `timestamp` > (SELECT MAX(`timestamp`) as x FROM {{ this }})
{% endif %}
