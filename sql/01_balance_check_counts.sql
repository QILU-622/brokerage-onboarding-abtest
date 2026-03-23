-- User-count breakdowns for baseline-balance review.
-- These outputs are the contingency-table inputs used for chi-square checks in Python.

SELECT experiment_group, channel, COUNT(*) AS users
FROM ab_assignment
GROUP BY 1, 2
ORDER BY 1, 2;

SELECT experiment_group, device_type, COUNT(*) AS users
FROM ab_assignment
GROUP BY 1, 2
ORDER BY 1, 2;

SELECT experiment_group, source_intent, COUNT(*) AS users
FROM ab_assignment
GROUP BY 1, 2
ORDER BY 1, 2;

SELECT experiment_group, age_band, COUNT(*) AS users
FROM ab_assignment
GROUP BY 1, 2
ORDER BY 1, 2;
