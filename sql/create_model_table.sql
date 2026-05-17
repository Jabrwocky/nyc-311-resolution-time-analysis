-- Rebuild the modeling table each time the pipeline runs so the SQLite output
-- always reflects the most recent cleaned service request data.
DROP TABLE IF EXISTS service_requests_model;

CREATE TABLE service_requests_model AS

-- Create a workload control for the statistical models.
-- This measures how many requests the same agency received in the same borough
-- on the same date, which helps separate geography effects from daily volume.
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

-- Add the workload feature back to each individual 311 request.
-- A LEFT JOIN preserves all cleaned service requests even if a workload value
-- is unexpectedly missing after aggregation.
SELECT
    r.*,
    w.daily_agency_borough_volume
FROM service_requests_clean AS r
LEFT JOIN daily_workload AS w
    ON r.created_date_only = w.created_date_only
    AND r.agency = w.agency
    AND r.borough = w.borough;
