DROP TABLE IF EXISTS service_requests_model;

CREATE TABLE service_requests_model AS
WITH daily_workload AS (
    SELECT
        created_date_only,
        agency,
        borough,
        COUNT(*) AS daily_agency_borough_volume
    FROM service_requests_clean
    GROUP BY
        created_date_only,
        agency,
        borough
)
SELECT
    r.*,
    w.daily_agency_borough_volume
FROM service_requests_clean AS r
LEFT JOIN daily_workload AS w
    ON r.created_date_only = w.created_date_only
    AND r.agency = w.agency
    AND r.borough = w.borough;