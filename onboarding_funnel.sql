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
    GROUP BY 1,2,3
)
SELECT * FROM step_users
ORDER BY experiment_group, step_no;
