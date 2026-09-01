# Brokerage App Onboarding A/B Test

A portfolio case study showing how Python, SQL, funnel analysis, and statistical inference can support a staged rollout decision for a redesigned brokerage-app onboarding journey.

**Independent portfolio project** · Python · SQL · A/B testing · funnel diagnostics · confidence intervals · rollout governance

[Live project](https://qilu-622.github.io/brokerage-onboarding-abtest/) · [Technical report](TECHNICAL_REPORT.md) · [Analysis notebook](notebooks/brokerage_abtest_analysis.ipynb) · [SQL queries](sql/abtest_queries.sql)

> **Data disclosure:** The dataset is entirely synthetic and was created solely for portfolio demonstration. It contains 46,218 simulated users and 221,046 simulated event records. It does not come from an internship, employer, client, brokerage, production system, or any confidential source.

## Decision question

After reducing form burden, improving process guidance, and clarifying key user questions, should the redesigned onboarding journey be expanded?

**Recommendation:** proceed to a channel-level staged rollout, but do not move directly to full release.

## Key synthetic experiment results

| Metric | Control | Treatment | Absolute change | 95% confidence interval |
|---|---:|---:|---:|---:|
| Account-opening completion | 16.82% | 21.55% | **+4.74 pp** | [4.02, 5.45] pp |
| 7-day retention | 35.23% | 37.09% | +1.86 pp | [0.98, 2.73] pp |
| 7-day first-deposit rate | 34.18% | 36.12% | +1.94 pp | [1.07, 2.81] pp |
| 7-day complaint rate | 1.277% | 1.280% | +0.00 pp | [-0.20, 0.21] pp |

The primary metric improved and the short-term quality metrics moved in the same direction, while the complaint-rate guardrail showed no statistically significant deterioration.

These figures come from a **synthetic portfolio experiment** and are not live business impact. The bundled redesign also does not isolate the contribution of each individual change, and long-term customer value remains unvalidated.

## Analytical approach

- User-level 50/50 randomisation.
- Sample-balance and experiment-validity checks.
- Funnel diagnosis across onboarding stages.
- Two-sample proportion tests and 95% confidence intervals.
- Channel heterogeneity analysis with multiple-testing control.
- Primary metrics, commercial quality metrics, and complaint guardrails.
- Staged-rollout recommendation with monitoring and rollback conditions.

## What this project demonstrates

- **Experiment analysis:** connects randomisation, balance checks, confidence intervals, and multiple-testing control.
- **Product diagnosis:** separates total funnel uplift from the specific steps where friction changed.
- **Commercial judgement:** reads completion, retention, first deposit, and complaints together instead of optimising one conversion metric.
- **Rollout governance:** translates the evidence into channel priorities, monitoring requirements, and rollback conditions.

## Run locally

```bash
git clone https://github.com/QILU-622/brokerage-onboarding-abtest.git
cd brokerage-onboarding-abtest

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

python -m pip install -r requirements.txt
python analysis.py
```

The script reads the example result tables in `results/` and prints the overall metric summary.

Optional regression checks:

```bash
python -m pip install -r requirements-dev.txt
pytest -q
```

## Repository guide

- [`index.html`](index.html): portfolio overview.
- [`reports/brokerage_abtest_report.html`](reports/brokerage_abtest_report.html): full experiment review.
- [`notebooks/brokerage_abtest_analysis.ipynb`](notebooks/brokerage_abtest_analysis.ipynb): analysis workflow.
- [`sql/abtest_queries.sql`](sql/abtest_queries.sql): core metric and validation queries.
- [`results/`](results/): example result tables.
- [`analysis.py`](analysis.py): command-line summary script.
- [`TECHNICAL_REPORT.md`](TECHNICAL_REPORT.md): methods, assumptions, results, limitations, and rollout logic.
- [`tests/test_summary.py`](tests/test_summary.py): regression checks for the published experiment summary.
- [`requirements.txt`](requirements.txt): Python dependencies.
- [`requirements-dev.txt`](requirements-dev.txt): optional test dependency.

## Decision boundary

The current evidence supports further staged testing, not immediate full rollout. Before expansion, the experiment should continue to verify allocation validity, process guardrails, contamination risk, cross-device identity handling, and longer-term value.
