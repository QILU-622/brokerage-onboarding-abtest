SELECT
    a.experiment_group,
    COUNT(*) AS users,
    ROUND(AVG(p.account_completed), 4) AS completion_rate,
    ROUND(AVG(p.retention_7d), 4) AS retention_7d,
    ROUND(AVG(p.complaint_7d), 4) AS complaint_7d,
    ROUND(AVG(p.first_deposit_7d), 4) AS first_deposit_7d
FROM ab_assignment a
JOIN post_metrics p
  ON a.user_id = p.user_id
GROUP BY 1;
