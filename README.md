# Brokerage App Onboarding A/B Test Evaluation  
## 券商 App 新客开户转化链路 A/B 实验评估

> **定位**：面向数据分析 / 增长分析 / 产品分析岗位的完整作品集项目。  
> **特点**：可复现、指标口径明确、方法链条完整、仓库结构与实际文件一致。  
> **边界**：所有数据均为 **synthetic data**，仅用于复现真实实验评估流程，不包含任何真实券商用户信息。

## 1. Business question / 业务问题

券商开户链路长、步骤多、信息负担重。这个项目模拟了一轮 user-level 随机分流实验，评估一组组合式流程优化——**表单精简 + 进度条提示 + 关键疑问解释**——是否能够显著提升开户完成率，同时不伤害用户体验护栏。

## 2. What this repo demonstrates / 这个仓库展示什么

- **Experiment design**：user-level randomization、primary/guardrail metrics、MDE awareness  
- **Statistical evaluation**：two-sample proportion tests、exact 95% CIs、Holm multiple-comparison correction  
- **Funnel diagnosis**：同时区分 cumulative reach 与 step-to-step conversion  
- **Business interpretation**：不只报显著性，还给出 rollout priority 与下一轮实验设计建议  
- **Reproducibility**：数据、SQL、Python、report、figures、notebook 全部在仓库中闭环  

## 3. Data scope / 数据范围

- Users: **46,218**
- Event logs: **221,046**
- Experiment window: **2026-01-01 to 2026-03-16**
- Groups: **Control = 23,256**, **Treatment = 22,962**

## 4. Headline results / 关键结果

| Metric | Control | Treatment | Uplift | 95% CI | p-value |
|---|---:|---:|---:|---:|---:|
| Account-open completion rate | 16.82% | 21.55% | +4.74 ppt | [4.02, 5.45] | < 0.001 |
| 7-day retention rate | 35.23% | 37.09% | +1.86 ppt | [0.98, 2.73] | < 0.001 |
| 7-day complaint rate | 1.28% | 1.28% | +0.00 ppt | [-0.20, 0.21] | 0.975 |
| 7-day first-deposit rate | 34.18% | 36.12% | +1.94 ppt | [1.07, 2.81] | < 0.001 |

## 5. Repository structure / 实际仓库结构

```text
brokerage-onboarding-abtest-improved/
├── analysis.py
├── index.html
├── requirements.txt
├── data/
├── docs/
├── figures/
├── notebooks/
├── reports/
├── results/
└── sql/
```

## 6. Reproduce / 复现方式

```bash
pip install -r requirements.txt
python analysis.py
```
