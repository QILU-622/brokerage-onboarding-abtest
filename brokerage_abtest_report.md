# 券商 App 新客开户转化链路 A/B 实验评估报告

## 1. Executive summary

本次实验评估的目标，是验证“表单精简 + 进度条提示 + 关键疑问解释”这一组流程优化，是否能够在不伤害体验护栏的前提下，显著提升券商 App 新客开户完成率。

实验结果显示：

- 开户完成率由 **16.82%** 提升至 **21.55%**，绝对 uplift **+4.74 ppt**，95% CI **[4.02, 5.45]**；
- 7 日留存率提升 **+1.86 ppt**，95% CI **[0.98, 2.73]**；
- 7 日投诉率变化 **+0.00 ppt**，95% CI **[-0.20, 0.21]**，未见显著恶化；
- 7 日首充率（探索性结果）提升 **+1.94 ppt**，95% CI **[1.07, 2.81]**。

因此，这轮 treatment 具备进入灰度上线的依据。

---

## 2. Business context

券商新客开户是典型的高摩擦业务流程。用户需要完成多步资料填写、身份验证、风险测评与绑卡操作。实际业务中，转化率提升并不只依赖最后一步的收口，而更依赖前中段是否能顺利推进。

本项目希望回答三个问题：

1. treatment 是否真的提升了开户完成率；
2. uplift 主要来自哪个步骤；
3. treatment 是否值得进入灰度上线，而不是继续停留在分析结论层面。

---

## 3. Experiment design

### 3.1 Randomisation

- Randomisation unit：**user-level**
- 分流比例：**50/50**
- Control：23,256
- Treatment：22,962

### 3.2 Observation window

- 时间范围：**2026-01-01 至 2026-03-16**
- 共 **75 天**

### 3.3 Metrics

**Primary metric**
- 开户完成率（account open completion rate）

**Guardrail metrics**
- 7 日留存率
- 7 日投诉率

**Exploratory metric**
- 7 日首充率

### 3.4 Statistical approach

- Balance check
- Funnel diagnosis
- Two-sample proportion test
- 95% confidence intervals
- Holm correction for channel-level comparison

### 3.5 Sample detection ability

在当前样本规模下，主指标在 **α = .05、80% power** 条件下可识别约 **0.99 ppt** 的绝对 uplift。本实验观察到的主指标 uplift 为 **4.74 ppt**，明显高于识别下限。

---

## 4. Balance check

渠道、设备、来源意图与年龄段分布未见显著失衡：

- channel p = 0.205
- device p = 0.286
- intent p = 0.421
- age p = 0.936

这意味着 treatment 与 control 的可比性较好，实验结果更有可能来自流程改动本身，而非样本结构偏差。

---

## 5. Overall results

| Metric | Control | Treatment | Diff | 95% CI | Interpretation |
|---|---:|---:|---:|---|---|
| 开户完成率 | 16.82% | 21.55% | **+4.74 ppt** | [4.02, 5.45] | 主指标显著提升 |
| 7 日留存率 | 35.23% | 37.09% | **+1.86 ppt** | [0.98, 2.73] | 留存同步改善 |
| 7 日投诉率 | 1.277% | 1.280% | +0.00 ppt | [-0.20, 0.21] | 未见显著恶化 |
| 7 日首充率 | 34.18% | 36.12% | **+1.94 ppt** | [1.07, 2.81] | 商业结果方向一致 |

### Interpretation

这个结果组合比单纯“主指标显著提升”更有业务价值：

- 主指标变好；
- 护栏没有明显受损；
- 留存与首充方向一致。

因此，这轮实验更像是**降低摩擦**，而不是通过误导、催促或压缩信息质量来获取短期转化。

---

## 6. Funnel diagnosis

### 6.1 Cumulative reach

Treatment 在多个阶段的累计 reach 均高于 control，说明整体链路推进更顺畅。

### 6.2 Step-to-step conversion

| Adjacent step | Control | Treatment | Diff |
|---|---:|---:|---:|
| Landing → Start onboarding | 80.50% | 80.79% | +0.29 ppt |
| Start → Submit basic info | 69.90% | 77.04% | **+7.14 ppt** |
| Submit basic info → ID pass | 81.60% | 83.73% | +2.13 ppt |
| ID pass → Risk assessment start | 74.41% | 78.81% | **+4.40 ppt** |
| Risk start → Risk complete | 72.90% | 78.01% | **+5.11 ppt** |
| Risk complete → Bind bank card | 81.72% | 82.35% | +0.64 ppt |
| Bind bank card → Complete | 82.63% | 81.69% | **-0.94 ppt** |

### 6.3 Diagnosis

这组结果说明：

1. **基础信息填写**是最明显的改善点，表单精简直接降低了放弃率；
2. **风险测评进入与完成**也明显提升，说明进度条提示与关键疑问解释有效减少了理解成本；
3. **最后一步并不是核心贡献来源**，甚至略有下降，说明整体 uplift 主要来自前中段流程推进，而非最后一步优化。

这类结论的价值在于，它把 uplift 与具体行为环节对应起来，而不只是停留在显著性结果。

---

## 7. Channel heterogeneity

| Channel | Control | Treatment | Uplift | Suggested action |
|---|---:|---:|---:|---|
| Referral | 19.95% | 25.60% | **+5.65 ppt** | 第一优先级灰度 |
| Paid social | 12.05% | 17.64% | **+5.59 ppt** | 第一优先级灰度 |
| Offline broker | 21.79% | 26.77% | +4.98 ppt | 第二优先级 |
| Content / SEO | 17.48% | 21.90% | +4.41 ppt | 第二优先级 |
| App store | 15.73% | 19.16% | +3.43 ppt | 保守推进 |

### Interpretation

各渠道 uplift 均为正，且在校正后仍显著。Referral 与 Paid social 的 uplift 最高，说明 treatment 对高摩擦来源更有效，适合作为优先灰度渠道。

---

## 8. Rollout recommendation

### Phase 1

优先在 **Referral + Paid social** 渠道灰度上线。

### Phase 2

若护栏稳定，再扩展到 Offline broker 与 Content / SEO。

### Guardrails during rollout

灰度期间应继续监控：

- 7 日投诉率
- 身份验证失败率
- 客服咨询量
- 首充率
- 高价值用户激活质量

### Why not immediate full rollout

因为当前 treatment 由多项改动打包构成，且开户链接属于受合规与服务资源约束较强的流程，直接全量上线会降低归因清晰度，也会扩大潜在风险暴露。

---

## 9. Potential business value

在缺少真实 ARPU / LTV 数据时，可用关键业务行为增量表达潜在价值，而不直接估算收入：

- 每 10 万 landing 用户，对应约新增 **4,736 个开户完成**；
- 每 10 万 landing 用户，对应约新增 **1,858 个 7 日留存用户**；
- 每 10 万 landing 用户，对应约新增 **1,940 个 7 日首充账户**。

这种表达聚焦关键业务行为增量，避免对财务结果做过度假设。

---

## 10. Limitations

- 数据为 synthetic data，仅用于复现实验评估框架；
- 当前 treatment 为多因素打包上线，只能识别组合效果；
- 7 日留存与 7 日首充为短期指标，无法替代长期价值；
- 当前结果未覆盖更长期的 LTV、交易活跃度与高价值用户结构变化。

---

## 11. Next steps

建议下一轮实验：

1. 拆解单因素测试：
   - 表单精简
   - 进度条提示
   - FAQ / 关键疑问解释
2. 补更多护栏：
   - 身份验证失败率
   - 客服咨询量
   - 风险问答中断率
3. 补长期指标：
   - 30 日留存
   - 首月入金
   - 首月交易活跃
   - 初始客群质量结构

---

## 12. Final takeaway

本项目的价值不只在于完成显著性检验，而在于把业务问题、实验设计、行为诊断、分层上线与下一步动作连接成完整链路：

- 有明确的业务问题；
- 有实验设计与护栏设置；
- 有严谨的结果汇报；
- 有行为层面的漏斗诊断；
- 有分层上线策略；
- 有后续实验规划。

相比单纯展示图表和 p 值，这种表达更能支持业务判断。
