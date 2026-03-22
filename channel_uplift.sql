SELECT
    a.channel,
    a.experiment_group,
    COUNT(*) AS users,
    ROUND(AVG(p.account_completed), 4) AS completion_rate
FROM ab_assignment a
JOIN post_metrics p
  ON a.user_id = p.user_id
GROUP BY 1,2
ORDER BY 1,2;
