from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"

METRIC_NAMES = {
    "开户完成率": "Account-opening completion",
    "7日留存率": "7-day retention",
    "7日投诉率": "7-day complaint rate",
    "7日首充率": "7-day first-deposit rate",
}

JUDGMENT_NAMES = {
    "支持继续灰度": "supports staged rollout",
    "短期质量同步改善": "short-term quality improved",
    "未见显著恶化": "no statistically significant deterioration",
    "商业方向一致": "commercial quality moved in the same direction",
}


def read_csv(name: str, results_dir: Path = RESULTS) -> list[dict[str, str]]:
    """Read one committed synthetic result table."""
    with (results_dir / name).open("r", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def load_overall_metrics(results_dir: Path = RESULTS) -> list[dict[str, str]]:
    """Load and validate the four published experiment metrics."""
    rows = read_csv("overall_metrics.csv", results_dir)
    required = {
        "metric",
        "control",
        "treatment",
        "uplift_ppt",
        "ci_95",
        "judgment",
    }
    if not rows:
        raise ValueError("overall_metrics.csv is empty")
    missing = required - rows[0].keys()
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    return rows


def format_metric(row: dict[str, str]) -> str:
    metric = METRIC_NAMES.get(row["metric"], row["metric"])
    judgment = JUDGMENT_NAMES.get(row["judgment"], row["judgment"])
    return (
        f"{metric}: control={row['control']} | treatment={row['treatment']} | "
        f"uplift={row['uplift_ppt']} pp | 95% CI={row['ci_95']} | "
        f"decision={judgment}"
    )


def main() -> None:
    print("Synthetic brokerage onboarding experiment")
    print("-" * 88)
    for row in load_overall_metrics():
        print(format_metric(row))
    print("-" * 88)
    print(
        "Boundary: synthetic portfolio experiment; "
        "not evidence of live brokerage performance."
    )


if __name__ == "__main__":
    main()
