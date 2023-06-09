WITH

  trading_dates AS (
    SELECT DISTINCT
      DATE(`timestamp`) as `date`
    FROM
      {{ source("stocks", "prices_hourly") }}
  ),

  timestamp_master AS (
    SELECT
      `timestamp`,
      DATE(`timestamp`) as `date`
    FROM
      UNNEST(
        GENERATE_TIMESTAMP_ARRAY(
          (SELECT TIMESTAMP(MIN(`date`)) FROM trading_dates), 
          CURRENT_TIMESTAMP(),
          INTERVAL 1 HOUR
          )
      ) AS `timestamp`
    WHERE
      EXTRACT(HOUR FROM `timestamp`) >= 0 AND EXTRACT(HOUR FROM `timestamp`) <= 6 -- Trading hours of ASX in UTC+0
  )

SELECT 
  * 
FROM 
  timestamp_master 
JOIN 
  trading_dates 
USING (`date`)
ORDER BY `timestamp`