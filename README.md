# Brokerage App Onboarding A/B Test Evaluation

## 券商 App 新客开户转化链路 A/B 实验评估

> 定位：面向数据分析 / 增长分析 / 产品分析岗位的完整作品集项目。  
> 特点：可复现、指标口径明确、方法链条完整、仓库结构与实际文件一致。  
> 边界：所有数据均为 synthetic data，仅用于复现真实实验评估流程，不包含任何真实券商用户信息。  

## 1. Business question / 业务问题

券商开户链路长、步骤多、信息负担重。这个项目模拟了一轮 user-level 随机分流实验，评估一组组合式流程优化——表单精简 + 进度条提示 + 关键疑问解释——是否能够显著提升开户完成率，同时不伤害用户体验护栏。

## 2. What this repo demonstrates / 这个仓库展示什么

- Experiment design：user-level randomization、primary/guardrail metrics、MDE awareness  
- Statistical evaluation：two-sample proportion tests、exact 95% CIs、Holm multiple-comparison correction  
- Funnel diagnosis：同时区分 cumulative reach 与 step-to-step conversion  
- Business interpretation：不只报显著性，还给出 rollout priority、有效性威胁与下一轮实验设计建议  
- Reproducibility：数据、SQL、Python、report、figures、notebook 全部在仓库中闭环  

## 3. Data scope / 数据范围

- Users: 46,218  
- Event logs: 221,046  
- Experiment window: 2026-01-01 to 2026-03-16  
- Groups: Control = 23,256, Treatment = 22,962  

## 4. Headline results / 关键结果

| Metric | Control | Treatment | Uplift | 95% CI | p-value |
|---|---:|---:|---:|---|---:|
| Account-open completion rate | 16.82% | 21.55% | +4.74 ppt | [4.02, 5.45] | < 0.001 |
| 7-day retention rate | 35.23% | 37.09% | +1.86 ppt | [0.98, 2.73] | < 0.001 |
| 7-day complaint rate | 1.28% | 1.28% | +0.00 ppt | [-0.20, 0.21] | 0.975 |
| 7-day first-deposit rate | 34.18% | 36.12% | +1.94 ppt | [1.07, 2.81] | < 0.001 |

## 5. Methods / 方法

1. Baseline balance check：对 `channel`、`device_type`、`source_intent`、`age_band` 做列联表检验。  
2. Overall treatment effect：对二元指标采用双样本比例 z 检验，并报告 unpooled 95% confidence intervals。  
3. Funnel diagnostics：同时报告 cumulative reach 和 step-to-step conversion，避免把两类漏斗口径混淆。  
4. Channel heterogeneity：按渠道分层估计 completion uplift，并使用 Holm correction 控制多重比较的 family-wise error。  
5. Sensitivity / detectability：基于已实现样本量估算完成率的近似 MDE。  

## 6. Validity threats / 实验风险与有效性威胁

这部分专门用于说明：为什么“有 uplift”不等于“可以不加审查地直接全量”。

### 6.1 SRM（Sample Ratio Mismatch）
- Control / Treatment 为 23,256 / 22,962，偏离理想 50/50 约 0.64%，当前看不到明显异常分流信号。  
- 但正式项目里，SRM 仍应是第一道健康检查：只要 assignment log、exposure log 与 analysis cohort 对不上，后续 uplift 的解释力就会显著下降。  

### 6.2 污染 / Interference
- 如果用户重复进入链路、跨渠道回流、被客服人工补救、或实验期内叠加其他运营触达，control 与 treatment 的暴露边界可能被稀释。  
- 正式落地时需要锁定首曝分组、对 user_id 去重，并尽量剔除人工介入造成的二次影响。  

### 6.3 跨设备 / Identity stitching
- 同一用户若在 mobile / web 或不同设备之间切换，而标识未正确合并，可能出现跨组暴露或步骤漏记。  
- 这类问题普通 balance check 抓不出来，正式分析应依赖稳定 account key 或 device graph 做 join。  

### 6.4 观察窗截断 / Mature-window censoring
- 实验截止到 2026-03-16，而 7 日留存、7 日首充要求完整成熟窗。  
- 尾部用户若未走满 7 天，会系统性低估 post metrics，因此正式结果应只保留 mature cohort，或明确 cohort 截尾规则。  

### 6.5 Novelty effect
- 进度条与 FAQ 解释类改动，早期可能因为“新鲜感”而短暂抬升启动率与风险问答完成率。  
- 如果 uplift 在灰度放量后快速回落，那么短期实验结果会高于长期稳定效果，因此需要按周跟踪 effect drift。  

## 7. Funnel diagnosis / 漏斗诊断

### Step-to-step conversion highlights
- Submit Basic Info：+7.14 ppt  
- Risk Assessment Start：+4.40 ppt  
- Risk Assessment Complete：+5.11 ppt  

这说明 treatment 主要降低了填写阻力与风险问答阻力，而不是单纯优化最后确认页。

### 反常结果解释：为什么最后一步略降，整体结论仍然成立
最后一步 `Bind bank card → Complete` 的 step conversion 为 **-0.94 ppt**，但这并不与整体 uplift 冲突，原因主要有三层：

1. **分母构成变化**：treatment 把更多中等意向用户推进到了更后面阶段，末端分母扩大后，最后一步的平均收口率可能被轻微摊薄。  
2. **末端摩擦未被直接触及**：当前改动主要作用于前中段认知负担；而末端开户完成更受 OTP、银行卡验证、KYC 复核、外部跳转等待等因素影响。  
3. **幅度大小不对称**：末端的 -0.94 ppt 明显小于前中段 +7.14 / +4.40 / +5.11 ppt 的提升，因此 end-to-end completion 仍然显著抬升。  

更成熟的解释不是“最后一步也优化了”，而是：当前 treatment 主要完成了“把用户更高比例地送到末端”，但末端收口摩擦本身仍然存在。

## 8. Channel heterogeneity / 渠道异质性

| Channel | Control / Treatment n | Uplift | 95% CI | Holm-adjusted p | Priority proxy |
|---|---:|---:|---|---:|---:|
| Referral | 4,156 / 4,070 | +5.65 ppt | [3.85, 7.46] | < 0.001 | 465 |
| Paid social | 5,991 / 6,026 | +5.59 ppt | [4.32, 6.86] | < 0.001 | 672 |
| Offline broker | 3,813 / 3,664 | +4.98 ppt | [3.04, 6.92] | < 0.001 | 372 |
| Content / SEO | 3,809 / 3,649 | +4.41 ppt | [2.61, 6.22] | < 0.001 | 329 |
| App store | 5,487 / 5,553 | +3.43 ppt | [2.02, 4.85] | < 0.001 | 379 |

## 9. Repository structure / 实际仓库结构

```text
brokerage-onboarding-abtest/
├── analysis.py
├── index.html
├── README.md
├── requirements.txt
├── data/
├── docs/
├── figures/
├── notebooks/
├── reports/
│   ├── brokerage_abtest_report.html
│   └── brokerage_abtest_report.md
├── results/
└── sql/
```

## 10. Reproduce / 复现方式

```bash
pip install -r requirements.txt
python analysis.py
```

## 11. Links / 链接

- 项目首页：<https://qilu-622.github.io/brokerage-onboarding-abtest/>
- 分析报告（HTML）：`reports/brokerage_abtest_report.html`
- Notebook：<https://github.com/QILU-622/brokerage-onboarding-abtest/blob/main/notebooks/brokerage_abtest_analysis.ipynb>
- SQL：<https://github.com/QILU-622/brokerage-onboarding-abtest/tree/main/sql>
