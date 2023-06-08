WITH

  prices AS (
    SELECT
      symbol,
      DATE(`timestamp`) as `date`,
      price,
      LAG(price) OVER (
        PARTITION BY symbol
        ORDER BY `timestamp`
      ) AS previous_price
    FROM
      {{ ref("prices_hourly_resampled") }}
    WHERE EXTRACT(HOUR FROM `timestamp`) = 6 -- Select daily close
  )

SELECT
  symbol,
  `date`,
  price,
  previous_price,
  AVG(price) OVER(
    PARTITION BY symbol
    ORDER BY `date`
    ROWS BETWEEN 30 PRECEDING AND CURRENT ROW
  ) as avg_price_30,
  STDDEV(price) OVER(
    PARTITION BY symbol
    ORDER BY `date`
    ROWS BETWEEN 30 PRECEDING AND CURRENT ROW
  ) as std_price_30,
  AVG(price - previous_price) OVER(
    PARTITION BY symbol
    ORDER BY `date`
    ROWS BETWEEN 30 PRECEDING AND CURRENT ROW
  ) as avg_return_30,
  STDDEV(price - previous_price) OVER(
    PARTITION BY symbol
    ORDER BY `date`
    ROWS BETWEEN 30 PRECEDING AND CURRENT ROW
  ) as std_return_30,
FROM
  prices
