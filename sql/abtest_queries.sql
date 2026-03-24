-- 券商 App 新客开户 A/B 实验核心查询
-- 说明：
-- 1. 这里使用示意性表结构；真实环境中请替换库表名与字段名。
-- 2. 所有 uplift 默认输出为绝对百分点变化（ppt）。

/* ---------------------------------------------------------
   1) assignment / exposure / outcome 基础闭环
--------------------------------------------------------- */
WITH assignment AS (
    SELECT
        user_id,
        experiment_group,
        assign_time::date AS assign_date
    FROM exp_assignment_log
    WHERE experiment_key = 'brokerage_onboarding_v2'
),
exposure AS (
    SELECT
        user_id,
        MIN(exposure_time) AS first_exposure_time
    FROM exp_exposure_log
    WHERE experiment_key = 'brokerage_onboarding_v2'
    GROUP BY 1
),
outcome AS (
    SELECT
        user_id,
        MAX(CASE WHEN event_name = 'account_open_complete' THEN 1 ELSE 0 END) AS is_complete,
        MAX(CASE WHEN event_name = 'retained_d7' THEN 1 ELSE 0 END) AS retained_d7,
        MAX(CASE WHEN event_name = 'first_deposit_d7' THEN 1 ELSE 0 END) AS first_deposit_d7,
        MAX(CASE WHEN event_name = 'complaint_d7' THEN 1 ELSE 0 END) AS complaint_d7
    FROM onboarding_event_log
    GROUP BY 1
)
SELECT
    a.experiment_group,
    COUNT(*) AS assigned_users,
    SUM(CASE WHEN e.user_id IS NOT NULL THEN 1 ELSE 0 END) AS exposed_users,
    SUM(COALESCE(o.is_complete, 0)) AS completed_users,
    AVG(COALESCE(o.is_complete, 0)::float) AS completion_rate,
    AVG(COALESCE(o.retained_d7, 0)::float) AS retention_d7_rate,
    AVG(COALESCE(o.first_deposit_d7, 0)::float) AS first_deposit_d7_rate,
    AVG(COALESCE(o.complaint_d7, 0)::float) AS complaint_d7_rate
FROM assignment a
LEFT JOIN exposure e USING (user_id)
LEFT JOIN outcome o USING (user_id)
GROUP BY 1
ORDER BY 1;

/* ---------------------------------------------------------
   2) Mature cohort：7 日后验指标只读取成熟 cohort
--------------------------------------------------------- */
SELECT
    experiment_group,
    COUNT(*) AS mature_users,
    AVG(retained_d7::float) AS retention_d7_rate,
    AVG(first_deposit_d7::float) AS first_deposit_d7_rate,
    AVG(complaint_d7::float) AS complaint_d7_rate
FROM user_outcome_daily
WHERE assign_date <= CURRENT_DATE - INTERVAL '7 day'
GROUP BY 1;

/* ---------------------------------------------------------
   3) Funnel：相邻步骤转化率
--------------------------------------------------------- */
WITH step_base AS (
    SELECT
        experiment_group,
        user_id,
        MAX(CASE WHEN event_name = 'landing' THEN 1 ELSE 0 END) AS landing,
        MAX(CASE WHEN event_name = 'start_onboarding' THEN 1 ELSE 0 END) AS start_onboarding,
        MAX(CASE WHEN event_name = 'submit_basic_info' THEN 1 ELSE 0 END) AS submit_basic_info,
        MAX(CASE WHEN event_name = 'id_pass' THEN 1 ELSE 0 END) AS id_pass,
        MAX(CASE WHEN event_name = 'risk_start' THEN 1 ELSE 0 END) AS risk_start,
        MAX(CASE WHEN event_name = 'risk_complete' THEN 1 ELSE 0 END) AS risk_complete,
        MAX(CASE WHEN event_name = 'bind_bank_card' THEN 1 ELSE 0 END) AS bind_bank_card,
        MAX(CASE WHEN event_name = 'account_open_complete' THEN 1 ELSE 0 END) AS completed
    FROM onboarding_event_log
    GROUP BY 1, 2
)
SELECT
    experiment_group,
    AVG(start_onboarding::float) / NULLIF(AVG(landing::float), 0) AS landing_to_start,
    AVG(submit_basic_info::float) / NULLIF(AVG(start_onboarding::float), 0) AS start_to_basic_info,
    AVG(id_pass::float) / NULLIF(AVG(submit_basic_info::float), 0) AS basic_info_to_id_pass,
    AVG(risk_start::float) / NULLIF(AVG(id_pass::float), 0) AS id_pass_to_risk_start,
    AVG(risk_complete::float) / NULLIF(AVG(risk_start::float), 0) AS risk_start_to_complete,
    AVG(bind_bank_card::float) / NULLIF(AVG(risk_complete::float), 0) AS risk_complete_to_bind_card,
    AVG(completed::float) / NULLIF(AVG(bind_bank_card::float), 0) AS bind_card_to_complete
FROM step_base
GROUP BY 1;

/* ---------------------------------------------------------
   4) 分渠道 uplift
--------------------------------------------------------- */
SELECT
    channel,
    experiment_group,
    COUNT(*) AS users,
    AVG(is_complete::float) AS completion_rate
FROM user_outcome_daily
GROUP BY 1, 2
ORDER BY 1, 2;

/* ---------------------------------------------------------
   5) 平衡性检查
--------------------------------------------------------- */
SELECT
    experiment_group,
    channel,
    device_type,
    intent_segment,
    age_bucket,
    COUNT(*) AS users
FROM user_profile_snapshot
GROUP BY 1, 2, 3, 4, 5
ORDER BY 2, 3, 4, 5, 1;

/* ---------------------------------------------------------
   6) 过程层护栏：OTP / 绑卡 / KYC / 风险问答中断 / 客服咨询
--------------------------------------------------------- */
SELECT
    experiment_group,
    AVG(CASE WHEN otp_result = 'fail' THEN 1 ELSE 0 END)::float AS otp_fail_rate,
    AVG(CASE WHEN bank_bind_result = 'fail' THEN 1 ELSE 0 END)::float AS bind_card_fail_rate,
    AVG(CASE WHEN kyc_review_result = 'fail' THEN 1 ELSE 0 END)::float AS kyc_fail_rate,
    AVG(CASE WHEN risk_interrupt = 1 THEN 1 ELSE 0 END)::float AS risk_interrupt_rate,
    AVG(CASE WHEN contacted_cs = 1 THEN 1 ELSE 0 END)::float AS customer_service_contact_rate
FROM onboarding_process_guardrail
GROUP BY 1;
