import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, norm
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"
FIGURES_DIR = ROOT / "figures"


def prop_diff_stats(success_a: int, n_a: int, success_b: int, n_b: int) -> dict:
    """Two-sample proportion z-test with unpooled 95% confidence interval."""
    p_a = success_a / n_a
    p_b = success_b / n_b
    diff = p_b - p_a
    pooled = (success_a + success_b) / (n_a + n_b)
    se = math.sqrt(pooled * (1 - pooled) * (1 / n_a + 1 / n_b))
    z = diff / se
    p_value = 2 * (1 - norm.cdf(abs(z)))
    se_unpooled = math.sqrt(p_a * (1 - p_a) / n_a + p_b * (1 - p_b) / n_b)
    ci_low = diff - 1.96 * se_unpooled
    ci_high = diff + 1.96 * se_unpooled
    return {
        "control_rate": p_a,
        "treatment_rate": p_b,
        "diff": diff,
        "z": z,
        "p_value": p_value,
        "ci_low": ci_low,
        "ci_high": ci_high,
    }


def holm_bonferroni(pvals: np.ndarray) -> np.ndarray:
    """Holm adjustment for multiple testing."""
    pvals = np.asarray(pvals)
    m = len(pvals)
    order = np.argsort(pvals)
    adjusted = np.empty(m)
    prev = 0.0
    for k, idx in enumerate(order):
        adj = (m - k) * pvals[idx]
        adj = max(adj, prev)
        adjusted[idx] = min(adj, 1.0)
        prev = adjusted[idx]
    return adjusted


def estimate_mde(control_rate: float, n_control: int, n_treatment: int,
                 alpha: float = 0.05, power_target: float = 0.80) -> float:
    """Approximate absolute MDE in rate space."""
    ratio = n_treatment / n_control
    solver = NormalIndPower()
    lo, hi = 1e-6, 0.10
    for _ in range(80):
        mid = (lo + hi) / 2
        effect_size = proportion_effectsize(control_rate, min(control_rate + mid, 0.999999))
        power = solver.power(
            effect_size=effect_size,
            nobs1=n_control,
            alpha=alpha,
            ratio=ratio,
            alternative="two-sided",
        )
        if power >= power_target:
            hi = mid
        else:
            lo = mid
    return hi


def main() -> None:
    RESULTS_DIR.mkdir(exist_ok=True)
    FIGURES_DIR.mkdir(exist_ok=True)

    assignment = pd.read_csv(DATA_DIR / "ab_assignment.csv", parse_dates=["assignment_time"])
    post = pd.read_csv(DATA_DIR / "post_metrics.csv")
    events = pd.read_csv(DATA_DIR / "onboarding_events.csv", parse_dates=["event_time"])
    ab = assignment.merge(post, on="user_id")

    summary = (
        ab.groupby("experiment_group")
        .agg(
            users=("user_id", "count"),
            completion_rate=("account_completed", "mean"),
            retention_7d=("retention_7d", "mean"),
            complaint_7d=("complaint_7d", "mean"),
            first_deposit_7d=("first_deposit_7d", "mean"),
            trade_count_7d=("trade_count_7d", "mean"),
        )
        .reset_index()
    )
    summary.to_csv(RESULTS_DIR / "experiment_summary.csv", index=False)

    control = ab[ab["experiment_group"] == "control"]
    treatment = ab[ab["experiment_group"] == "treatment"]

    metric_map = {
        "account_completed": "Account-open completion rate",
        "retention_7d": "7-day retention rate",
        "complaint_7d": "7-day complaint rate",
        "first_deposit_7d": "7-day first-deposit rate",
    }

    overall_rows = []
    for metric, label in metric_map.items():
        stats = prop_diff_stats(
            int(control[metric].sum()),
            len(control),
            int(treatment[metric].sum()),
            len(treatment),
        )
        overall_rows.append(
            {
                "metric": metric,
                "metric_label": label,
                "control_success": int(control[metric].sum()),
                "control_n": len(control),
                "treatment_success": int(treatment[metric].sum()),
                "treatment_n": len(treatment),
                **stats,
                "diff_ppt": stats["diff"] * 100,
                "ci_low_ppt": stats["ci_low"] * 100,
                "ci_high_ppt": stats["ci_high"] * 100,
            }
        )
    pd.DataFrame(overall_rows).to_csv(RESULTS_DIR / "overall_effects.csv", index=False)

    balance_rows = []
    for col in ["channel", "device_type", "source_intent", "age_band"]:
        tab = pd.crosstab(assignment["experiment_group"], assignment[col])
        chi2, p, dof, _ = chi2_contingency(tab)
        balance_rows.append({"dimension": col, "chi2": chi2, "dof": dof, "p_value": p})
    pd.DataFrame(balance_rows).to_csv(RESULTS_DIR / "balance_check_pvalues.csv", index=False)

    success_events = events[events["status"] == "success"].merge(
        assignment[["user_id", "experiment_group"]], on="user_id", how="left"
    )
    funnel = (
        success_events.groupby(["experiment_group", "step_no", "event_name"])["user_id"]
        .nunique()
        .reset_index(name="users")
        .sort_values(["step_no", "experiment_group"])
    )
    totals = summary.set_index("experiment_group")["users"].to_dict()
    funnel["group_total"] = funnel["experiment_group"].map(totals)
    funnel["rate_from_start"] = funnel["users"] / funnel["group_total"]
    funnel["step_to_step_rate"] = funnel.groupby("experiment_group")["users"].transform(lambda s: s / s.shift(1))
    funnel.loc[funnel["step_no"] == 1, "step_to_step_rate"] = np.nan
    funnel.to_csv(RESULTS_DIR / "funnel_reach.csv", index=False)

    channel_rows = []
    for channel, df in ab.groupby("channel"):
        c = df[df["experiment_group"] == "control"]
        t = df[df["experiment_group"] == "treatment"]
        stats = prop_diff_stats(
            int(c["account_completed"].sum()),
            len(c),
            int(t["account_completed"].sum()),
            len(t),
        )
        channel_rows.append(
            {
                "channel": channel,
                "n_control": len(c),
                "n_treatment": len(t),
                **stats,
                "diff_ppt": stats["diff"] * 100,
                "ci_low_ppt": stats["ci_low"] * 100,
                "ci_high_ppt": stats["ci_high"] * 100,
            }
        )
    channel_df = pd.DataFrame(channel_rows).sort_values("diff_ppt", ascending=False).reset_index(drop=True)
    channel_df["holm_p"] = holm_bonferroni(channel_df["p_value"].to_numpy())
    channel_df.to_csv(RESULTS_DIR / "channel_effects.csv", index=False)

    control_rate = summary.loc[summary["experiment_group"] == "control", "completion_rate"].iloc[0]
    mde = estimate_mde(control_rate, len(control), len(treatment))
    print(f"Approximate MDE for completion rate at alpha=.05 and 80%% power: {mde*100:.2f} ppt")


if __name__ == "__main__":
    main()
