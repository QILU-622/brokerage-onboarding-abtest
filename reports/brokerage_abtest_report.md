# Brokerage App 新客开户 A/B 实验评估报告

> 定位：一个可复现的 synthetic-data 作品集案例，用来展示增长分析 / 产品分析岗位在实验评估中的完整工作流。  
> 边界：所有数据均为合成模拟数据，不包含任何真实券商用户信息，也不声称代表真实券商经营结果。  

## 1. 业务问题

券商 App 新客开户链路长、摩擦点多，业务希望验证一组组合式流程优化——表单精简 + 进度条提示 + 关键疑问解释——是否能够显著提升开户完成率，同时不伤害体验质量指标。

## 2. 数据与实验范围

- 样本量：46,218 名新客  
- 事件日志：221,046 条  
- 实验期：2026-01-01 至 2026-03-16（75 天）  
- 随机化单位：user-level 50/50 assignment  
- 对照组 / 实验组：23,256 / 22,962  

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
| 7-day retention rate | Guardrail metric | 用户分流后 7 天内仍有回访 / 活跃记录的比例 |
| 7-day complaint rate | Guardrail metric | 用户分流后 7 天内出现投诉记录的比例 |
| 7-day first-deposit rate | Secondary business-quality metric | 用户分流后 7 天内完成首次入金的比例 |

## 4. 方法

1. Baseline balance check：对 `channel`、`device_type`、`source_intent`、`age_band` 做列联表检验。  
2. Overall treatment effect：对二元指标采用双样本比例 z 检验，并报告 unpooled 95% confidence intervals。  
3. Funnel diagnostics：同时报告 cumulative reach 和 step-to-step conversion，避免把两类漏斗口径混淆。  
4. Channel heterogeneity：按渠道分层估计 completion uplift，并使用 Holm correction 控制多重比较的 family-wise error。  
5. Sensitivity / detectability：基于已实现样本量估算完成率的近似 MDE。  

## 5. 基线平衡性

各主要分层变量均未见显著失衡：

- `channel`: p = 0.205  
- `device_type`: p = 0.286  
- `source_intent`: p = 0.421  
- `age_band`: p = 0.936  

## 6. 实验风险与有效性威胁

### 6.1 SRM（Sample Ratio Mismatch）
Control / Treatment 为 23,256 / 22,962，偏离理想 50/50 约 0.64%，当前看不到明显异常分流信号。  
但正式项目里，SRM 仍应是第一道健康检查：若 assignment log、exposure log 与最终 analysis cohort 不一致，后续 uplift 解释将显著失真。

### 6.2 污染 / Interference
如果用户重复进入链路、跨渠道回流、被客服人工补救、或实验期叠加其他运营触达，control 与 treatment 的暴露边界可能被稀释。  
正式落地时需要锁定首曝分组、对 user_id 去重，并尽量剔除人工介入造成的二次影响。

### 6.3 跨设备 / Identity stitching
同一用户若在 mobile / web 或不同设备之间切换，而标识未正确合并，可能出现跨组暴露或步骤漏记。  
这类问题普通 balance check 抓不出来，因此正式分析应依赖稳定 account key 或 device graph 完成 join。

### 6.4 观察窗截断 / Mature-window censoring
实验截止到 2026-03-16，而 7 日留存、7 日首充要求完整成熟窗。  
尾部用户若未走满 7 天，会系统性低估 post metrics，因此正式结果应只保留 mature cohort，或明确 cohort 截尾规则。

### 6.5 Novelty effect
进度条与 FAQ 解释类改动，早期可能因为“新鲜感”而短暂抬升启动率与风险问答完成率。  
如果 uplift 在灰度放量后快速回落，那么短期实验结果会高于长期稳定效果，因此需要按周跟踪 effect drift。

### 6.6 为什么要显性写出这些风险
更成熟的实验复盘，不只是证明“有显著 uplift”，还要说明“结果为什么值得信、为什么当前只建议灰度而非直接全量”。

## 7. 总体效果

| Metric | Control | Treatment | Uplift | 95% CI | p-value |
|---|---:|---:|---:|---|---:|
| Account-open completion rate | 16.82% | 21.55% | +4.74 ppt | [4.02, 5.45] | < 0.001 |
| 7-day retention rate | 35.23% | 37.09% | +1.86 ppt | [0.98, 2.73] | < 0.001 |
| 7-day complaint rate | 1.28% | 1.28% | +0.00 ppt | [-0.20, 0.21] | 0.975 |
| 7-day first-deposit rate | 34.18% | 36.12% | +1.94 ppt | [1.07, 2.81] | < 0.001 |

## 8. 漏斗诊断

### 8.1 关键 uplift 来源
- Submit Basic Info：+7.14 ppt  
- Risk Assessment Start：+4.40 ppt  
- Risk Assessment Complete：+5.11 ppt  

这说明 treatment 主要降低了填写阻力与风险问答阻力，而不是单纯优化最后确认页。

### 8.2 反常结果解释：为什么最后一步略降，整体结论仍然成立
最后一步 `Bind bank card → Complete` 的 step conversion 为 **-0.94 ppt**，但这并不与整体 uplift 冲突，原因主要有三层：

1. **分母构成变化**：treatment 把更多中等意向用户推进到了更后面阶段，末端分母扩大后，最后一步的平均收口率可能被轻微摊薄。  
2. **末端摩擦未被直接触及**：当前改动主要作用于前中段认知负担；而末端开户完成更受 OTP、银行卡验证、KYC 复核、外部跳转等待等因素影响。  
3. **幅度大小不对称**：末端的 -0.94 ppt 明显小于前中段 +7.14 / +4.40 / +5.11 ppt 的提升，因此 end-to-end completion 仍然显著抬升。  

更成熟的解释不是“最后一步也优化了”，而是：当前 treatment 主要完成了“把用户更高比例地送到末端”，但末端收口摩擦本身仍然存在。

## 9. 渠道异质性

| Channel | Control / Treatment n | Uplift | 95% CI | Holm-adjusted p | Priority proxy |
|---|---:|---:|---|---:|---:|
| Referral | 4,156 / 4,070 | +5.65 ppt | [3.85, 7.46] | < 0.001 | 465 |
| Paid social | 5,991 / 6,026 | +5.59 ppt | [4.32, 6.86] | < 0.001 | 672 |
| Offline broker | 3,813 / 3,664 | +4.98 ppt | [3.04, 6.92] | < 0.001 | 372 |
| Content / SEO | 3,809 / 3,649 | +4.41 ppt | [2.61, 6.22] | < 0.001 | 329 |
| App store | 5,487 / 5,553 | +3.43 ppt | [2.02, 4.85] | < 0.001 | 379 |

## 10. 局限性

1. 这是 synthetic-data 作品集案例，不应把数值本身当作真实券商经营结论。  
2. 当前 treatment 是组合式改动，只能识别组合效果，不能识别单个设计元素的独立贡献。  
3. 7-day retention 与 first-deposit 只代表短期质量，不替代长期交易活跃、LTV 或合规风险结果。  
4. Detectability 展示的是已实现样本规模下的近似 MDE，不等同于正式项目中的事前 power plan。  
5. 本报告新增了 SRM、污染、跨设备、成熟窗截断与 novelty effect 讨论，目的是补足“结果可信度”层面的分析，而不是宣称这些威胁已由现有 synthetic data 完全排除。  

## 11. 下一步建议

- 拆解单因素测试：表单精简 / 进度条 / FAQ 解释。  
- 新增护栏：身份验证失败率、客服咨询量、风险问答中断率。  
- 新增日志：assignment log、exposure log、客服人工介入标签、cross-device stitching 质量标记。  
- 新增分层：新老客、设备类型、来源意图、是否高价值潜客。  
- 补长期指标：首月入金、首月交易活跃、30 日留存，并按周跟踪 novelty effect 的 effect drift。  

## 12. 复现方式

```bash
pip install -r requirements.txt
python analysis.py
```
