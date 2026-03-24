# 券商 App 新客开户实验复盘

## 项目链接

- 项目主页：<https://qilu-622.github.io/brokerage-onboarding-abtest/>
- 分析报告：`reports/brokerage_abtest_report.html`
- Notebook：<https://github.com/QILU-622/brokerage-onboarding-abtest/blob/main/notebooks/brokerage_abtest_analysis.ipynb>
- SQL：<https://github.com/QILU-622/brokerage-onboarding-abtest/tree/main/sql>

## 概览

该项目围绕券商 App 新客开户链路展开，重点回答三个问题：

1. 流程差异是否支持继续放量；
2. 提升主要发生在哪些环节；
3. 不同渠道的放量顺序如何安排。

## 关键结论

- 开户完成率：16.82% → 21.55%，绝对提升 +4.74 ppt。
- 7 日留存率：+1.86 ppt。
- 7 日投诉率：未见显著恶化。
- 7 日首充率：+1.94 ppt。
- 放量顺序：推荐渠道与付费投放优先，其次线下客户经理与内容/搜索，应用商店保守推进。

## 仓库结构

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

## 复现

```bash
pip install -r requirements.txt
python analysis.py
```

## 数据说明

页面与报告使用脱敏模拟日志重建分析流程，用于说明指标体系、验证路径与决策边界；不对应任何真实机构经营结果或客户数据。
