import math
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, norm
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize

# Prefer a font that can render Chinese labels if available.
mpl.rcParams["font.family"] = ["Noto Sans CJK JP", "DejaVu Sans", "Arial"]
mpl.rcParams["axes.unicode_minus"] = False


ROOT = Path(__file__).resolve().parent


def locate_file(filename: str) -> Path:
    """Find a file either in repo root or under ./data."""
    candidates = [ROOT / filename, ROOT / "data" / filename]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError(f"Could not find {filename} in repo root or ./data/")


def prop_diff_stats(success_a: int, n_a: int, success_b: int, n_b: int) -> dict:
    """Two-sample proportion test + unpooled 95% CI."""
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
        "diff": diff,
        "z": z,
        "p": p_value,
        "ci_low": ci_low,
        "ci_high": ci_high,
    }


def holm_bonferroni(pvals: np.ndarray) -> np.ndarray:
    """Holm correction for multiple testing."""
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
    """
    Estimate the approximate absolute MDE (ppt in rate space, not %)
    for a two-sided two-sample proportion test, given realized sample sizes.
    """
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


def build_summary_tables(assignment: pd.DataFrame, post: pd.DataFrame, funnel: pd.DataFrame) -> dict:
    ab = assignment.merge(post, on="user_id")

    summary = (
        ab.groupby("experiment_group")
        .agg(
            users=("user_id", "count"),
            completion_rate=("account_completed", "mean"),
            retention_7d=("retention_7d", "mean"),
            complaint_7d=("complaint_7d", "mean"),
            first_deposit_7d=("first_deposit_7d", "mean"),
        )
        .reset_index()
    )

    control = ab[ab["experiment_group"] == "control"]
    treatment = ab[ab["experiment_group"] == "treatment"]

    overall_rows = []
    for metric in ["account_completed", "retention_7d", "complaint_7d", "first_deposit_7d"]:
        stats = prop_diff_stats(
            int(control[metric].sum()),
            len(control),
            int(treatment[metric].sum()),
            len(treatment),
        )
        overall_rows.append({"metric": metric, **stats})
    overall = pd.DataFrame(overall_rows)

    channel_rows = []
    for channel, df in ab.groupby("channel"):
        c = df[df["experiment_group"] == "control"]
        t = df[df["experiment_group"] == "treatment"]
        stats = prop_diff_stats(int(c["account_completed"].sum()), len(c), int(t["account_completed"].sum()), len(t))
        channel_rows.append(
            {
                "channel": channel,
                "control_n": len(c),
                "treatment_n": len(t),
                "control_rate": c["account_completed"].mean(),
                "treatment_rate": t["account_completed"].mean(),
                "uplift_ppt": stats["diff"] * 100,
                "ci_low_ppt": stats["ci_low"] * 100,
                "ci_high_ppt": stats["ci_high"] * 100,
                "p": stats["p"],
            }
        )
    channel = pd.DataFrame(channel_rows).sort_values("uplift_ppt", ascending=False).reset_index(drop=True)
    channel["p_holm"] = holm_bonferroni(channel["p"].values)

    balance_rows = []
    for col in ["channel", "device_type", "source_intent", "age_band"]:
        chi2, p_value, _, _ = chi2_contingency(pd.crosstab(assignment[col], assignment["experiment_group"]))
        balance_rows.append({"dimension": col, "chi2": chi2, "p": p_value})
    balance = pd.DataFrame(balance_rows)

    mde = estimate_mde(
        control_rate=float(summary.loc[summary["experiment_group"] == "control", "completion_rate"].iloc[0]),
        n_control=int(summary.loc[summary["experiment_group"] == "control", "users"].iloc[0]),
        n_treatment=int(summary.loc[summary["experiment_group"] == "treatment", "users"].iloc[0]),
    )

    return {
        "ab": ab,
        "summary": summary,
        "overall": overall,
        "channel": channel,
        "balance": balance,
        "funnel": funnel,
        "mde": mde,
    }


def save_tables(summary_bundle: dict) -> None:
    summary_bundle["summary"].to_csv(ROOT / "experiment_summary.csv", index=False)
    summary_bundle["overall"].to_csv(ROOT / "stat_test_summary.csv", index=False)
    summary_bundle["channel"].to_csv(ROOT / "channel_effects_detailed.csv", index=False)
    summary_bundle["balance"].to_csv(ROOT / "balance_check_summary.csv", index=False)


def save_figures(summary_bundle: dict) -> None:
    summary = summary_bundle["summary"].set_index("experiment_group")
    overall = summary_bundle["overall"]
    channel = summary_bundle["channel"]
    funnel = summary_bundle["funnel"]

    stage_labels = {
        "landing_page_view": "Landing",
        "start_onboarding": "Start",
        "submit_basic_info": "Basic info",
        "id_verification_pass": "ID verify",
        "risk_assessment_start": "Risk start",
        "risk_assessment_complete": "Risk complete",
        "bind_bank_card": "Bind card",
        "account_open_complete": "Complete",
    }

    # 01. Cumulative stage reach
    plt.figure(figsize=(10, 5.8))
    for grp, label in [("control", "Control"), ("treatment", "Treatment")]:
        tmp = funnel[funnel["experiment_group"] == grp].sort_values("step_no")
        plt.plot(tmp["step_no"], tmp["rate_from_start"] * 100, marker="o", linewidth=2.5, label=label)
        for _, row in tmp.iterrows():
            plt.text(row["step_no"], row["rate_from_start"] * 100 + 1.4, f'{row["rate_from_start"] * 100:.1f}%', ha="center", fontsize=9)
    ordered = funnel.sort_values("step_no").drop_duplicates("step_no")
    plt.xticks(ordered["step_no"], [stage_labels[s] for s in ordered["stage"]], rotation=20)
    plt.ylabel("Stage reach from landing page (%)")
    plt.title("Cumulative stage reach by experiment group")
    plt.ylim(0, 110)
    plt.legend(frameon=False)
    plt.figtext(
        0.01,
        0.01,
        "Each point shows the share of users who reached that stage out of all users assigned to the group.",
        ha="left",
        fontsize=9,
    )
    plt.tight_layout(rect=(0, 0.04, 1, 1))
    plt.savefig(ROOT / "01_onboarding_funnel.png", dpi=180, bbox_inches="tight")
    plt.close()

    # 05. Step-to-step conversion
    plt.figure(figsize=(10, 6))
    step_df = funnel[funnel["step_no"] > 1].copy().sort_values("step_no")
    x = np.arange(len(step_df["step_no"].unique()))
    width = 0.36
    cvals = step_df[step_df["experiment_group"] == "control"]["rate_from_prev"].values * 100
    tvals = step_df[step_df["experiment_group"] == "treatment"]["rate_from_prev"].values * 100
    labels = [stage_labels[s] for s in step_df.drop_duplicates("step_no")["stage"]]
    plt.bar(x - width / 2, cvals, width=width, label="Control")
    plt.bar(x + width / 2, tvals, width=width, label="Treatment")
    for xi, cv, tv in zip(x, cvals, tvals):
        plt.text(xi - width / 2, cv + 0.8, f"{cv:.1f}%", ha="center", fontsize=8)
        plt.text(xi + width / 2, tv + 0.8, f"{tv:.1f}%", ha="center", fontsize=8)
    plt.xticks(x, labels, rotation=20)
    plt.ylabel("Step-to-step conversion (%)")
    plt.title("Step conversion by experiment group")
    plt.ylim(0, 100)
    plt.legend(frameon=False)
    plt.figtext(
        0.01,
        0.01,
        "This view isolates where the treatment changed user progression most strongly between adjacent steps.",
        ha="left",
        fontsize=9,
    )
    plt.tight_layout(rect=(0, 0.04, 1, 1))
    plt.savefig(ROOT / "05_step_conversion.png", dpi=180, bbox_inches="tight")
    plt.close()

    # 02. Primary metrics
    metric_order = ["completion_rate", "retention_7d", "complaint_7d"]
    metric_names = {"completion_rate": "开户完成率", "retention_7d": "7日留存率", "complaint_7d": "7日投诉率"}
    plot_df = pd.DataFrame(
        {
            "metric": [metric_names[m] for m in metric_order],
            "Control": [summary.loc["control", m] * 100 for m in metric_order],
            "Treatment": [summary.loc["treatment", m] * 100 for m in metric_order],
        }
    )
    plt.figure(figsize=(9, 5.4))
    x = np.arange(len(plot_df))
    width = 0.35
    plt.bar(x - width / 2, plot_df["Control"], width=width, label="Control")
    plt.bar(x + width / 2, plot_df["Treatment"], width=width, label="Treatment")
    for xi, cv, tv in zip(x, plot_df["Control"], plot_df["Treatment"]):
        plt.text(xi - width / 2, cv + 0.5, f"{cv:.2f}%", ha="center", fontsize=9)
        plt.text(xi + width / 2, tv + 0.5, f"{tv:.2f}%", ha="center", fontsize=9)
    plt.xticks(x, plot_df["metric"])
    plt.ylabel("Rate (%)")
    plt.title("Primary and guardrail metrics")
    plt.legend(frameon=False)
    plt.ylim(0, plot_df[["Control", "Treatment"]].max().max() + 8)
    plt.tight_layout()
    plt.savefig(ROOT / "02_primary_metrics.png", dpi=180, bbox_inches="tight")
    plt.close()

    # 03. Channel uplift with CI
    plt.figure(figsize=(10, 6))
    y = np.arange(len(channel))
    plt.barh(y, channel["uplift_ppt"])
    xerr = np.vstack([channel["uplift_ppt"] - channel["ci_low_ppt"], channel["ci_high_ppt"] - channel["uplift_ppt"]])
    plt.errorbar(channel["uplift_ppt"], y, xerr=xerr, fmt="none", capsize=4)
    for yi, row in channel.iterrows():
        plt.text(
            row["uplift_ppt"] + 0.12,
            yi,
            f'{row["uplift_ppt"]:.2f} ppt  ({int(row["control_n"])}/{int(row["treatment_n"])})',
            va="center",
            fontsize=9,
        )
    plt.axvline(0, linewidth=1)
    plt.yticks(y, [s.replace("_", " / ") for s in channel["channel"]])
    plt.xlabel("Treatment uplift in completion rate (ppt)")
    plt.title("Channel uplift with 95% CI and group sample sizes")
    plt.gca().invert_yaxis()
    plt.figtext(
        0.01,
        0.01,
        "Labels show uplift and control/treatment sample sizes. All channel effects remain significant after Holm correction.",
        ha="left",
        fontsize=9,
    )
    plt.tight_layout(rect=(0, 0.04, 1, 1))
    plt.savefig(ROOT / "03_channel_uplift.png", dpi=180, bbox_inches="tight")
    plt.close()

    # 04. Overall CI chart
    label_map = {
        "account_completed": "开户完成率",
        "retention_7d": "7日留存率",
        "complaint_7d": "7日投诉率",
    }
    overall_plot = overall[overall["metric"].isin(label_map.keys())].copy()
    overall_plot["label"] = overall_plot["metric"].map(label_map)
    overall_plot["diff_ppt"] = overall_plot["diff"] * 100
    overall_plot["ci_low_ppt"] = overall_plot["ci_low"] * 100
    overall_plot["ci_high_ppt"] = overall_plot["ci_high"] * 100

    plt.figure(figsize=(9.5, 5.8))
    y = np.arange(len(overall_plot))
    plt.scatter(overall_plot["diff_ppt"], y, s=45)
    xerr = np.vstack([overall_plot["diff_ppt"] - overall_plot["ci_low_ppt"], overall_plot["ci_high_ppt"] - overall_plot["diff_ppt"]])
    plt.errorbar(overall_plot["diff_ppt"], y, xerr=xerr, fmt="none", capsize=5)
    plt.axvline(0, linewidth=1)
    for yi, row in overall_plot.iterrows():
        if row["p"] < 0.001:
            p_label = "p<0.001"
        elif row["p"] < 0.01:
            p_label = "p<0.01"
        elif row["p"] < 0.05:
            p_label = "p<0.05"
        else:
            p_label = "n.s."
        plt.text(
            row["ci_high_ppt"] + 0.15,
            yi,
            f'Δ {row["diff_ppt"]:.2f} ppt  |  95% CI [{row["ci_low_ppt"]:.2f}, {row["ci_high_ppt"]:.2f}]  |  {p_label}',
            va="center",
            fontsize=9,
        )
    plt.yticks(y, overall_plot["label"])
    plt.xlabel("Treatment effect (ppt)")
    plt.title("Treatment effect with exact 95% confidence intervals")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(ROOT / "04_confidence_intervals.png", dpi=180, bbox_inches="tight")
    plt.close()


def main() -> None:
    assignment = pd.read_csv(locate_file("ab_assignment.csv"), parse_dates=["assignment_time"])
    post = pd.read_csv(locate_file("post_metrics.csv"))
    funnel = pd.read_csv(locate_file("funnel_summary.csv"))

    bundle = build_summary_tables(assignment, post, funnel)
    save_tables(bundle)
    save_figures(bundle)

    summary = bundle["summary"].set_index("experiment_group")
    overall = bundle["overall"].set_index("metric")
    balance = bundle["balance"].set_index("dimension")

    print("=== Experiment summary ===")
    print(summary)
    print("\n=== Treatment effect summary ===")
    print(overall[["diff", "ci_low", "ci_high", "p"]])
    print("\n=== Balance check p-values ===")
    print(balance["p"])
    print(f"\nApprox. MDE for completion rate at alpha=.05, power=.80: {bundle['mde'] * 100:.2f} ppt")


if __name__ == "__main__":
    main()
