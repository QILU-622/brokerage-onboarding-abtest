-- Adjacent-step conversion. This is different from cumulative reach.
WITH step_users AS (
    SELECT
        a.experiment_group,
        e.step_no,
        e.event_name,
        COUNT(DISTINCT e.user_id) AS users
    FROM onboarding_events e
    JOIN ab_assignment a
      ON e.user_id = a.user_id
    WHERE e.status = 'success'
    GROUP BY 1, 2, 3
),
step_conversion AS (
    SELECT
        experiment_group,
        step_no,
        event_name,
        users,
        LAG(users) OVER (
            PARTITION BY experiment_group
            ORDER BY step_no
        ) AS previous_step_users
    FROM step_users
)
SELECT
    experiment_group,
    step_no,
    event_name,
    users,
    previous_step_users,
    CASE
        WHEN previous_step_users IS NULL THEN NULL
        ELSE ROUND(1.0 * users / previous_step_users, 4)
    END AS step_to_step_rate
FROM step_conversion
ORDER BY experiment_group, step_no;
