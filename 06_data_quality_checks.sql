-- Basic reproducibility and data-quality checks.
SELECT COUNT(*) AS assignment_rows, COUNT(DISTINCT user_id) AS distinct_users
FROM ab_assignment;

SELECT COUNT(*) AS post_metric_rows, COUNT(DISTINCT user_id) AS distinct_users
FROM post_metrics;

SELECT
    COUNT(*) AS event_rows,
    COUNT(DISTINCT user_id) AS distinct_users,
    MIN(event_time) AS min_event_time,
    MAX(event_time) AS max_event_time
FROM onboarding_events;

SELECT
    SUM(CASE WHEN a.user_id IS NULL THEN 1 ELSE 0 END) AS events_without_assignment
FROM onboarding_events e
LEFT JOIN ab_assignment a
  ON e.user_id = a.user_id;
