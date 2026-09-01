from analysis import format_metric, load_overall_metrics


def test_published_primary_metric() -> None:
    rows = load_overall_metrics()
    primary = next(row for row in rows if row["metric"] == "开户完成率")

    assert primary["control"] == "16.82%"
    assert primary["treatment"] == "21.55%"
    assert primary["uplift_ppt"] == "+4.74"
    assert primary["ci_95"] == "[4.02, 5.45]"


def test_summary_is_english_first() -> None:
    rows = load_overall_metrics()
    rendered = format_metric(rows[0])

    assert rendered.startswith("Account-opening completion:")
    assert "supports staged rollout" in rendered
