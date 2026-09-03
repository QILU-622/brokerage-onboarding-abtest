# Technical Report: Brokerage App Onboarding A/B Test

## 1. Project scope and ownership

This is an independent synthetic portfolio project. I designed the experiment review, metric framework, funnel diagnosis, statistical checks, channel rollout logic, and decision boundaries. No employer, internship, client, brokerage, production, customer, or confidential data were used.

The synthetic dataset contains 46,218 simulated users and 221,046 simulated event records. The dates, channels, behaviours, and outcomes exist only to reproduce the analytical workflow.

## 2. Decision problem

The treatment combines lower form burden, clearer process guidance, and better explanations of common user questions. The decision is whether the combined redesign should move into a staged rollout without buying conversion at the cost of retention, complaints, or operational pressure.

## 3. Experiment design

| Element | Design |
|---|---|
| Randomisation unit | User-level 50/50 assignment |
| Sample | 23,256 control users; 22,962 treatment users |
| Observation window | 75 days |
| Primary metric | Account-opening completion |
| Quality metrics | 7-day retention; 7-day first-deposit rate |
| Guardrail | 7-day complaint rate |
| Inference | Two-sample proportion tests and 95% confidence intervals |
| Heterogeneity | Channel-level effects with Holm multiple-testing correction |

## 4. Main results

| Metric | Control | Treatment | Absolute change | 95% confidence interval |
|---|---:|---:|---:|---:|
| Account-opening completion | 16.82% | 21.55% | +4.74 pp | [4.02, 5.45] pp |
| 7-day retention | 35.23% | 37.09% | +1.86 pp | [0.98, 2.73] pp |
| 7-day first-deposit rate | 34.18% | 36.12% | +1.94 pp | [1.07, 2.81] pp |
| 7-day complaint rate | 1.277% | 1.280% | +0.00 pp | [-0.20, 0.21] pp |

The primary metric improves, short-term quality metrics move in the same direction, and the complaint-rate interval does not show a material deterioration. On this synthetic evidence, the correct decision is a staged rollout rather than immediate full release.

## 5. Funnel diagnosis

The largest improvement occurs between onboarding start and basic-information submission. Risk-assessment steps also improve. The final bank-card-to-completion step declines slightly, indicating that the treatment reduces early and middle-stage friction but does not resolve OTP, bank verification, KYC review, or external-redirect delays.

This matters because total conversion can improve while a later operational bottleneck remains hidden. The next experiment should separate form simplification, progress guidance, and FAQ placement instead of attributing the full uplift to one component.

## 6. Implementation and quality checks

The Python implementation does not simply print the pre-formatted summary. It reads the committed success counts and sample sizes, recomputes group rates, absolute uplift, unpooled 95% confidence intervals, pooled z-statistics, and two-sided p-values, and reconciles them with the detailed result table.

Seven automated tests cover the published primary result, the complete four-metric set, metric roles, the multiplicity policy, English decision output, inference fields, and invalid sample sizes or success counts. GitHub Actions reruns the analysis and tests on Python 3.11 and 3.12 after each repository change.

## 7. Multiplicity policy

The four overall outcomes are deliberately not corrected as one family because they have different inferential roles:

- Account-opening completion is the single pre-specified primary outcome, so there is only one confirmatory efficacy test.
- Retention and first deposit are supporting quality and commercial evidence, not additional co-primary success claims.
- Complaints are a harm guardrail. Pooling this test with efficacy outcomes would make the harm check less sensitive and increase the chance of missing deterioration.
- The five channel effects are same-status exploratory subgroup hypotheses. Holm correction is applied across that family to control the family-wise error rate without assuming independence.

This asymmetry is therefore intentional rather than an omission. If a future experiment promoted several outcomes to co-primary success criteria, the analysis plan would pre-specify a testing hierarchy, gatekeeping procedure, or multiplicity correction for that confirmatory family.

## 8. Validity and decision boundary

- The treatment is a bundle, so the current analysis cannot isolate each component's causal contribution.
- Seven-day outcomes are short-term proxies; 30-day retention, deposits, trading activity, and lifetime value remain untested.
- Assignment, exposure, and outcome logs must form a complete chain before scaling.
- Cross-device identity, channel re-entry, manual remediation, and treatment contamination require monitoring.
- Process guardrails should include OTP failure, bank-card binding failure, KYC review failure, support contacts, and complaint categories.

The results are synthetic and are not evidence of live brokerage performance. They demonstrate the analytical process used to move from experiment data to a guarded operating decision.
