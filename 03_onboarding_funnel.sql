-- Cumulative funnel reach from landing-page start.
WITH success_events AS (
    SELECT
        a.experiment_group,
        e.step_no,
        e.event_name,
        e.user_id
    FROM onboarding_events e
    JOIN ab_assignment a
      ON e.user_id = a.user_id
    WHERE e.status = 'success'
),
step_users AS (
    SELECT
        experiment_group,
        step_no,
        event_name,
        COUNT(DISTINCT user_id) AS users
    FROM success_events
    GROUP BY 1, 2, 3
),
group_totals AS (
    SELECT
        experiment_group,
        COUNT(*) AS assigned_users
    FROM ab_assignment
    GROUP BY 1
)
SELECT
    s.experiment_group,
    s.step_no,
    s.event_name,
    s.users,
    g.assigned_users,
    ROUND(1.0 * s.users / g.assigned_users, 4) AS rate_from_start
FROM step_users s
JOIN group_totals g
  ON s.experiment_group = g.experiment_group
ORDER BY s.experiment_group, s.step_no;
