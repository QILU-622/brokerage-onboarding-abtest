# 券商 App 新客开户 A/B 实验复盘

核心业务判断：**这轮流程优化是否足以支持继续买量，并且不会以质量或服务成本为代价。**

线上页：<https://qilu-622.github.io/brokerage-onboarding-abtest/>  
分析报告：`reports/brokerage_abtest_report.html`

---

## 当前结论

当前证据支持继续推进，但**不建议直接全量**。

- 开户完成率：16.82% → 21.55%，绝对提升 **+4.74 ppt**
- 7 日留存率：35.23% → 37.09%，绝对提升 **+1.86 ppt**
- 7 日投诉率：未见显著恶化
- 7 日首充率：34.18% → 36.12%，绝对提升 **+1.94 ppt**

建议先在 uplift 更高、业务弹性更强的渠道灰度推进，再在结果稳定后决定最终上线范围。

---

## 这是一个怎样的 A/B 实验

- **Control（对照组）**：原开户流程
- **Treatment（实验组）**：本轮优化后的组合版本
- **分流方式**：用户层级 50/50 随机分流
- **主指标**：开户完成率
- **护栏指标**：7 日留存率、7 日投诉率
- **次级指标**：7 日首充率
- **判读规则**：统一使用绝对百分点变化（ppt）和 95% 置信区间；上线节奏同时参考质量指标与风险检查

这里使用随机对照实验评估版本净效果，结果直接用于 rollout 决策。

---

## 仓库导航

- `index.html`：项目主页，包含决策摘要与上线判断
- `reports/brokerage_abtest_report.html`：详细分析报告，包含实验设置、证据检查、机制拆解与 rollout 方案
- `notebooks/`：分析 notebook
- `sql/`：SQL 查询
- `figures/`：图表资源
- `data/`：样本数据与中间结果
- `results/`：汇总输出
- `analysis.py`：分析脚本

---

## 项目结构

```text
brokerage-onboarding-abtest/
├── assets/
│   └── site.css
├── data/
├── figures/
├── notebooks/
├── reports/
│   └── brokerage_abtest_report.html
├── results/
├── sql/
├── analysis.py
├── index.html
└── README.md
```

---

## 页面结构

### 主页包含 5 个部分

1. 实验设置与判读规则
2. 是否支持继续推进
3. 当前证据是否足够可信
4. uplift 主要来自哪里
5. 分渠道 rollout 方案

### 报告页包含 5 类信息

1. 实验设置与判读规则
2. 指标树与可信度检查
3. 漏斗机制拆解与动作建议
4. 分渠道 rollout 规则
5. 风险、护栏与下一轮实验优先级

---

## 发布方式

如果这是 GitHub Pages 仓库，替换以下文件后即可发布更新：

- `index.html`
- `assets/site.css`
- `reports/brokerage_abtest_report.html`
- `README.md`

提交后等待 Pages 重新部署，再强制刷新页面查看效果。

---

## 数据备注

页面数值来自脱敏重建场景，不对应任何实际机构经营数据。所有百分比变化均为绝对百分点变化（ppt）。
