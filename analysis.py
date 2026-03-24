from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"

def read_csv(name: str) -> list[dict[str, str]]:
    with open(RESULTS / name, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def main() -> None:
    overall = read_csv("overall_metrics.csv")
    print("整体指标摘要")
    print("-" * 72)
    for row in overall:
        print(
            f"{row['metric']}: control={row['control']} | treatment={row['treatment']} | "
            f"uplift={row['uplift_ppt']} ppt | 95% CI={row['ci_95']} | judgment={row['judgment']}"
        )

if __name__ == "__main__":
    main()
