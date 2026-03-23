-- Channel-level completion-rate uplift inputs.
WITH joined AS (
    SELECT
        a.channel,
        a.experiment_group,
        p.account_completed
    FROM ab_assignment a
    JOIN post_metrics p
      ON a.user_id = p.user_id
)
SELECT
    channel,
    experiment_group,
    COUNT(*) AS users,
    SUM(account_completed) AS completed_users,
    ROUND(AVG(account_completed), 4) AS completion_rate
FROM joined
GROUP BY 1, 2
ORDER BY channel, experiment_group;
