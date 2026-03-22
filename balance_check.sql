SELECT
    experiment_group,
    channel,
    device_type,
    source_intent,
    COUNT(*) AS users
FROM ab_assignment
GROUP BY 1,2,3,4
ORDER BY 1,2,3,4;
