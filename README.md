# 券商 App 新客开户 A/B 实验复盘｜灰度上线决策

本项目围绕一个核心问题展开：当开户链路的表单负担、流程提示和关键疑问解释被同时优化后，这组改动是否值得继续放量，以及应如何控制上线风险。

## 目录结构

- `index.html`：项目主页，面向作品集展示。
- `reports/brokerage_abtest_report.html`：分析报告，面向完整复盘。
- `notebooks/brokerage_abtest_analysis.ipynb`：分析 Notebook，展示分析流程。
- `sql/abtest_queries.sql`：核心口径 SQL。
- `results/*.csv`：示例结果表。
- `analysis.py`：读取结果文件并输出摘要。
- `requirements.txt`：本地复现环境依赖。

## 当前业务判断

建议进入分渠道灰度，暂不建议直接全量。

原因：

1. 开户完成率 uplift 为 +4.74 ppt，95% 置信区间不跨 0；
2. 7 日留存率与 7 日首充率方向一致；
3. 7 日投诉率未见显著恶化；
4. 组合式改版尚未拆清单因子贡献，过程层护栏与实验有效性仍需继续复核。

## 使用方式

直接将本仓库文件覆盖到 GitHub Pages 仓库根目录即可。当前版本不依赖外部图表库，页面资源均为本地文件或内嵌样式，适合静态托管。
