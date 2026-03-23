# Brokerage App 新客开户 A/B 实验评估报告

> **定位**：一个可复现的 synthetic-data 作品集案例，用来展示增长分析 / 产品分析岗位在实验评估中的完整工作流。  
> **边界**：所有数据均为合成模拟数据，不包含任何真实券商用户信息，也不声称代表真实券商经营结果。

## 1. 业务问题

券商 App 新客开户链路长、摩擦点多，业务希望验证一组组合式流程优化——**表单精简 + 进度条提示 + 关键疑问解释**——是否能够显著提升开户完成率，同时不伤害体验质量指标。

## 2. 数据与实验范围

- 样本量：**46,218** 名新客
- 事件日志：**221,046** 条
- 实验期：**2026-01-01 至 2026-03-16（75 天）**
- 随机化单位：**user-level 50/50 assignment**
- 对照组 / 实验组：**23,256 / 22,962**

### 2.1 数据表

| 表名 | 粒度 | 关键字段 | 用途 |
|---|---|---|---|
| `ab_assignment.csv` | user | `experiment_group`, `channel`, `device_type`, `source_intent`, `age_band` | 分流、分层与基线平衡性检查 |
| `onboarding_events.csv` | event | `event_name`, `step_no`, `status`, `dwell_seconds` | 漏斗与步骤级诊断 |
| `post_metrics.csv` | user | `account_completed`, `retention_7d`, `complaint_7d`, `first_deposit_7d`, `trade_count_7d` | 主指标、护栏指标与下游业务质量指标 |

## 3. 指标定义

| 指标 | 角色 | 定义 |
|---|---|---|
| Account-open completion rate | Primary metric | 用户在观察窗口内完成开户的比例 |
| 7-day retention rate | Guardrail metric | 用户分流后 7 天内仍有回访/活跃记录的比例 |
| 7-day complaint rate | Guardrail metric | 用户分流后 7 天内出现投诉记录的比例 |
| 7-day first-deposit rate | Secondary business-quality metric | 用户分流后 7 天内完成首次入金的比例 |

## 4. 方法

1. **Baseline balance check**：对 `channel`、`device_type`、`source_intent`、`age_band` 做列联表检验。  
2. **Overall treatment effect**：对二元指标采用双样本比例 z 检验，并报告 **unpooled 95% confidence intervals**。  
3. **Funnel diagnostics**：同时报告 cumulative reach 和 step-to-step conversion，避免把两类漏斗口径混淆。  
4. **Channel heterogeneity**：按渠道分层估计 completion uplift，并使用 **Holm correction** 控制多重比较的 family-wise error。  
5. **Sensitivity / detectability**：基于已实现样本量估算完成率的近似 MDE。

## 5. 基线平衡性

各主要分层变量均未见显著失衡：

- `channel`: p = 0.205
- `device_type`: p = 0.286
- `source_intent`: p = 0.421
- `age_band`: p = 0.936

## 6. 总体效果

| Metric | Control | Treatment | Uplift | 95% CI | p-value |
|---|---:|---:|---:|---:|---:|
| Account-open completion rate | 16.82% | 21.55% | +4.74 ppt | [4.02, 5.45] | < 0.001 |
| 7-day retention rate | 35.23% | 37.09% | +1.86 ppt | [0.98, 2.73] | < 0.001 |
| 7-day complaint rate | 1.28% | 1.28% | +0.00 ppt | [-0.20, 0.21] | 0.975 |
| 7-day first-deposit rate | 34.18% | 36.12% | +1.94 ppt | [1.07, 2.81] | < 0.001 |

## 7. 漏斗诊断

- Submit Basic Info：+7.14 ppt  
- Risk Assessment Start：+4.40 ppt  
- Risk Assessment Complete：+5.11 ppt  

这说明 treatment 主要降低了填写阻力与风险问答阻力，而不是单纯优化最后确认页。

## 8. 渠道异质性

| Channel | Control / Treatment n | Uplift | 95% CI | Holm-adjusted p | Priority proxy |
|---|---:|---:|---:|---:|---:|
| Referral | 4,156 / 4,070 | +5.65 ppt | [3.85, 7.46] | < 0.001 | 465 |
| Paid social | 5,991 / 6,026 | +5.59 ppt | [4.32, 6.86] | < 0.001 | 672 |
| Offline broker | 3,813 / 3,664 | +4.98 ppt | [3.04, 6.92] | < 0.001 | 372 |
| Content / SEO | 3,809 / 3,649 | +4.41 ppt | [2.61, 6.22] | < 0.001 | 329 |
| App store | 5,487 / 5,553 | +3.43 ppt | [2.02, 4.85] | < 0.001 | 379 |


## 9. 局限性

1. 这是 synthetic-data 作品集案例，不应把数值本身当作真实券商经营结论。  
2. 当前 treatment 是组合式改动，只能识别组合效果，不能识别单个设计元素的独立贡献。  
3. 7-day retention 与 first-deposit 只代表短期质量，不替代长期交易活跃、LTV 或合规风险结果。  
4. Detectability 展示的是已实现样本规模下的近似 MDE，不等同于正式项目中的事前 power plan。  

## 10. 复现方式

```bash
pip install -r requirements.txt
python analysis.py
```
