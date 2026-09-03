from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
Z_95 = 1.96

METRIC_NAMES = {
    "account_completed": "Account-opening completion",
    "retention_7d": "7-day retention",
    "complaint_7d": "7-day complaint rate",
    "first_deposit_7d": "7-day first-deposit rate",
}

DECISIONS = {
    "account_completed": "supports staged rollout",
    "retention_7d": "short-term quality improved",
    "complaint_7d": "no statistically significant deterioration",
    "first_deposit_7d": "commercial quality moved in the same direction",
}

METRIC_ROLES = {
    "account_completed": "pre-specified primary outcome",
    "retention_7d": "supporting quality outcome",
    "complaint_7d": "harm guardrail",
    "first_deposit_7d": "supporting commercial outcome",
}

MULTIPLICITY_POLICY = (
    "Overall outcomes are not one confirmatory hypothesis family: completion is the "
    "single pre-specified primary outcome, retention and first deposit are supporting "
    "evidence, and complaints are a harm guardrail. Pooling the guardrail with efficacy "
    "tests would reduce sensitivity to harm. Holm correction is reserved for the five "
    "same-status channel heterogeneity tests."
)

REQUIRED_COLUMNS = {
    "metric",
    "control_success",
    "control_n",
    "treatment_success",
    "treatment_n",
    "control_rate",
    "treatment_rate",
    "diff",
    "z",
    "p_value",
    "ci_low",
    "ci_high",
}


@dataclass(frozen=True)
class MetricResult:
    """A recomputed two-sample proportion result for one outcome."""

    metric: str
    control_success: int
    control_n: int
    treatment_success: int
    treatment_n: int
    control_rate: float
    treatment_rate: float
    difference: float
    ci_low: float
    ci_high: float
    z_score: float
    p_value: float


def read_csv(name: str, results_dir: Path = RESULTS) -> list[dict[str, str]]:
    """Read one committed synthetic result table."""
    with (results_dir / name).open("r", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def calculate_proportion_effect(
    control_success: int,
    control_n: int,
    treatment_success: int,
    treatment_n: int,
) -> tuple[float, float, float, float, float, float, float]:
    """Calculate rates, uplift, an unpooled CI, and a pooled z-test."""
    for label, success, sample_size in (
        ("control", control_success, control_n),
        ("treatment", treatment_success, treatment_n),
    ):
        if sample_size <= 0:
            raise ValueError(f"{label}_n must be positive")
        if not 0 <= success <= sample_size:
            raise ValueError(
                f"{label}_success must be between 0 and {label}_n"
            )

    control_rate = control_success / control_n
    treatment_rate = treatment_success / treatment_n
    difference = treatment_rate - control_rate

    ci_se = math.sqrt(
        control_rate * (1 - control_rate) / control_n
        + treatment_rate * (1 - treatment_rate) / treatment_n
    )
    ci_low = difference - Z_95 * ci_se
    ci_high = difference + Z_95 * ci_se

    pooled_rate = (control_success + treatment_success) / (
        control_n + treatment_n
    )
    test_se = math.sqrt(
        pooled_rate * (1 - pooled_rate) * (1 / control_n + 1 / treatment_n)
    )
    z_score = difference / test_se if test_se else 0.0
    p_value = math.erfc(abs(z_score) / math.sqrt(2))

    return (
        control_rate,
        treatment_rate,
        difference,
        ci_low,
        ci_high,
        z_score,
        p_value,
    )


def _assert_matches_source(
    metric: str, field: str, calculated: float, source: str
) -> None:
    if not math.isclose(calculated, float(source), abs_tol=1e-12):
        raise ValueError(
            f"{metric}: recomputed {field} does not match the committed table"
        )


def load_overall_metrics(results_dir: Path = RESULTS) -> list[MetricResult]:
    """Recompute the published effects from success counts and sample sizes."""
    rows = read_csv("overall_effects.csv", results_dir)
    if not rows:
        raise ValueError("overall_effects.csv is empty")

    missing = REQUIRED_COLUMNS - rows[0].keys()
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    results: list[MetricResult] = []
    for row in rows:
        metric = row["metric"]
        if metric not in METRIC_NAMES:
            raise ValueError(f"Unknown metric: {metric}")

        control_success = int(row["control_success"])
        control_n = int(row["control_n"])
        treatment_success = int(row["treatment_success"])
        treatment_n = int(row["treatment_n"])
        (
            control_rate,
            treatment_rate,
            difference,
            ci_low,
            ci_high,
            z_score,
            p_value,
        ) = calculate_proportion_effect(
            control_success,
            control_n,
            treatment_success,
            treatment_n,
        )

        for field, calculated in (
            ("control_rate", control_rate),
            ("treatment_rate", treatment_rate),
            ("diff", difference),
            ("ci_low", ci_low),
            ("ci_high", ci_high),
            ("z", z_score),
            ("p_value", p_value),
        ):
            _assert_matches_source(metric, field, calculated, row[field])

        results.append(
            MetricResult(
                metric=metric,
                control_success=control_success,
                control_n=control_n,
                treatment_success=treatment_success,
                treatment_n=treatment_n,
                control_rate=control_rate,
                treatment_rate=treatment_rate,
                difference=difference,
                ci_low=ci_low,
                ci_high=ci_high,
                z_score=z_score,
                p_value=p_value,
            )
        )
    return results


def _format_rate(metric: str, value: float) -> str:
    decimals = 3 if metric == "complaint_7d" else 2
    return f"{value:.{decimals}%}"


def format_metric(result: MetricResult) -> str:
    """Render one recomputed result as an English decision summary."""
    return (
        f"{METRIC_NAMES[result.metric]}: "
        f"role={METRIC_ROLES[result.metric]} | "
        f"control={_format_rate(result.metric, result.control_rate)} | "
        f"treatment={_format_rate(result.metric, result.treatment_rate)} | "
        f"uplift={result.difference * 100:+.2f} pp | "
        f"95% CI=[{result.ci_low * 100:.2f}, {result.ci_high * 100:.2f}] pp | "
        f"p={result.p_value:.3g} | decision={DECISIONS[result.metric]}"
    )


def main() -> None:
    print("Synthetic brokerage onboarding experiment")
    print("-" * 100)
    for result in load_overall_metrics():
        print(format_metric(result))
    print("-" * 100)
    print(f"Multiplicity policy: {MULTIPLICITY_POLICY}")
    print("-" * 100)
    print(
        "Boundary: synthetic portfolio experiment; "
        "not evidence of live brokerage performance."
    )


if __name__ == "__main__":
    main()
