# 券商 App 新客开户转化链路 A/B 实验评估与用户痛点归因

> 面向数据分析 / 增长分析岗位的完整作品集项目。  
> 数据为**合成模拟数据（synthetic data）**，仅用于复现真实实验评估流程，不包含任何真实券商用户数据。

## 1. 业务背景
券商 App 新客开户链路较长，表单填写和风险测评阶段流失严重。项目模拟了一个随机分流 A/B 实验，对比原始流程和“表单精简 + 进度条提示 + 关键疑问解释”方案，验证是否能提升开户完成率，并同步监控护栏指标。

## 2. 数据范围
- 新客样本：46,218 名
- 事件日志：221,046 条
- 主要表：`ab_assignment.csv`、`onboarding_events.csv`、`post_metrics.csv`

## 3. 实验设计
- Control：原始开户流程
- Treatment：表单精简 + 进度条提示 + 关键疑问解释
- 主指标：开户完成率
- 护栏指标：7 日留存率、7 日投诉率
- 方法：样本平衡性检查、漏斗拆解、双样本比例检验、渠道分层 uplift

## 4. 关键发现
- 开户完成率从 **16.82%** 提升到 **21.55%**，绝对提升 **4.74pct**，差异显著。
- 7 日留存率提升 **1.86pct**。
- 投诉率从 **1.28%** 到 **1.28%**，差异不显著。
- 渠道分层显示 `referral` 渠道 uplift 最高，约 **5.65pct**，说明高流失来源更适合优先灰度上线。

## 5. 可交付物
- SQL 查询：`sql/`
- Python 复现脚本：`analysis.py`
- Notebook：`notebooks/brokerage_abtest_analysis.ipynb`
- 图表：`figures/`
- 结果报告：`reports/brokerage_abtest_report.md`
- 静态展示页：`portfolio/index.html`

## 6. 目录结构
```text
brokerage-onboarding-abtest/
├── data/
├── figures/
├── notebooks/
├── reports/
├── sql/
├── portfolio/
├── analysis.py
└── README.md
```

## 7. 运行方式
```bash
python analysis.py
```

