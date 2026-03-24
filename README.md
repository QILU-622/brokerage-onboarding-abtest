# Brokerage App Onboarding Experiment Review

## 券商 App 新客开户实验复盘与灰度上线决策

> 这是一个面向业务分析 / 数据分析 / 增长分析岗位的实验复盘案例。  
> 重点不是“做出显著性”，而是把实验结果转成业务动作：**是否值得放量、效果来自哪里、为什么当前建议先灰度而不是直接全量。**  
> 数据为 synthetic data，仅用于复现真实实验分析与上线决策流程，不包含任何真实券商用户信息。

## 1. 项目要回答什么问题

券商 App 新客开户链路通常包含基础资料填写、身份校验、风险测评、绑卡与开户注册等多个高摩擦步骤。  
如果前中段流程过长、说明不清、理解成本过高，用户往往不会真正走到末端，也就谈不上后续留存与入金。

本项目评估一组组合式流程优化——**表单精简 + 进度条提示 + 关键疑问解释**——是否能：

- 提升开户完成率
- 不伤害体验护栏
- 为后续留存与首充带来正向信号
- 支持“先灰度、再拆因”的产品决策

## 2. 决策摘要

### 推荐动作
**建议进入分渠道灰度，不建议直接全量。**

### 为什么值得灰度
- 主指标开户完成率从 **16.82%** 提升到 **21.55%**，绝对 uplift 为 **+4.74 ppt**，95% CI 为 **[4.02, 5.45]**
- 7 日留存率同步提升 **+1.86 ppt**
- 7 日投诉率无显著恶化
- 7 日首充率方向一致，提供了早期商业价值信号

### 为什么不直接全量
- 当前 treatment 是**多因素打包改动**，只能确认组合效果，不能直接确认每个设计元素的独立贡献
- 上线前后仍需继续验证 **SRM、污染、跨设备识别、成熟窗截断、novelty effect**
- 更稳妥的做法是：**先灰度验证稳定性，再拆单因素实验做归因**

## 3. 关键发现：uplift 主要来自哪里

本轮 uplift 的核心不是“最后一步收口改善”，而是**前中段摩擦下降**：

| Step-to-step conversion | Control | Treatment | Change |
|---|---:|---:|---:|
| Landing → Start onboarding | 80.50% | 80.79% | +0.29 ppt |
| Start → Submit basic info | 69.90% | 77.04% | **+7.14 ppt** |
| Submit basic info → ID pass | 81.60% | 83.73% | +2.13 ppt |
| ID pass → Risk assessment start | 74.41% | 78.81% | **+4.40 ppt** |
| Risk start → Risk complete | 72.90% | 78.01% | **+5.11 ppt** |
| Risk complete → Bind bank card | 81.72% | 82.35% | +0.64 ppt |
| Bind bank card → Complete | 82.63% | 81.69% | -0.94 ppt |

### 解释
- **最大贡献点**：基础信息提交阶段，说明表单精简有效降低了填写阻力
- **第二贡献点**：进入风险测评与完成风险测评阶段，说明进度提示与 FAQ 解释降低了理解成本
- **末端略降但整体仍成立**：treatment 把更多中等意向用户推进到末端，扩大了最后一步分母；同时末端 OTP / KYC / 绑卡校验等摩擦并未被当前改动直接解决，因此末端收口率小幅回落并不推翻整体正向结论

## 4. 实验设计

- **Randomization**：user-level 50/50 分流
- **Groups**：Control = 23,256；Treatment = 22,962
- **Window**：2026-01-01 至 2026-03-16，共 75 天
- **Users**：46,218
- **Event logs**：221,046

### 指标体系
- **Primary**：开户完成率
- **Guardrails**：7 日留存率、7 日投诉率
- **Exploratory**：7 日首充率

### 统计方法
- Baseline balance check
- Two-sample proportion z test
- Unpooled 95% confidence intervals
- 渠道分层 uplift + Holm 多重比较校正
- 基于已实现样本量的近似 MDE 估算

## 5. Headline results

| Metric | Control | Treatment | Uplift | 95% CI | Interpretation |
|---|---:|---:|---:|---|---|
| Account-open completion rate | 16.82% | 21.55% | +4.74 ppt | [4.02, 5.45] | 主指标显著提升 |
| 7-day retention rate | 35.23% | 37.09% | +1.86 ppt | [0.98, 2.73] | 体验质量同步改善 |
| 7-day complaint rate | 1.277% | 1.280% | +0.00 ppt | [-0.20, 0.21] | 无显著恶化 |
| 7-day first-deposit rate | 34.18% | 36.12% | +1.94 ppt | [1.07, 2.81] | 商业结果方向一致 |

## 6. 渠道分层与灰度优先级

| Channel | Control | Treatment | Uplift | Recommendation |
|---|---:|---:|---:|---|
| Referral | 19.95% | 25.60% | +5.65 ppt | 第一优先级灰度 |
| Paid social | 12.05% | 17.64% | +5.59 ppt | 第一优先级灰度 |
| Offline broker | 21.79% | 26.77% | +4.98 ppt | 第二优先级 |
| Content / SEO | 17.48% | 21.90% | +4.41 ppt | 第二优先级 |
| App store | 15.73% | 19.16% | +3.43 ppt | 保守推进 |

**灰度逻辑：**
1. 先在 uplift 更高、回报更直接的渠道验证稳定性  
2. 继续监控投诉率、身份验证失败率、客服咨询量、首充率与高价值用户质量  
3. 稳定后再扩大流量，并拆解单因素实验

## 7. Validity threats / 为什么不能只看“显著”

当前结论支持“可以进入灰度”，但还不足以支持“可以不加审查地直接全量”。

### 需要继续控制的风险
- **SRM（Sample Ratio Mismatch）**
- **污染 / Interference**
- **跨设备 / Identity stitching**
- **观察窗截断 / Mature-window censoring**
- **Novelty effect**

这部分的意义不是否定 uplift，而是把结论推进到更接近真实业务复盘的层次：

> 结果成立是一层；结果为什么值得信、能不能放量，是另一层。

## 8. 仓库内容

- `index.html`：作品集主页
- `README.md`：仓库首页说明
- `reports/brokerage_abtest_report.md` / `.html`：完整报告
- `notebooks/brokerage_abtest_analysis.ipynb`：分析 notebook
- `sql/`：SQL 查询
- `analysis.py`：分析脚本
- `figures/`：图表资源

## 9. 项目一句话口径（适合面试 / 简历）

围绕券商 App 新客开户链路，搭建并复盘一轮 user-level A/B 实验，基于漏斗诊断、分层 uplift、置信区间与实验风险评估，判断 treatment 值得进入分渠道灰度，并识别 uplift 主要来自基础信息填写与风险测评阶段的摩擦下降，而非末端收口改善。
