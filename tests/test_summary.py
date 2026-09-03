import math

import pytest

from analysis import (
    METRIC_ROLES,
    MULTIPLICITY_POLICY,
    calculate_proportion_effect,
    format_metric,
    load_overall_metrics,
)


def test_primary_metric_is_recomputed_from_counts() -> None:
    results = load_overall_metrics()
    primary = next(
        result for result in results if result.metric == "account_completed"
    )

    assert primary.control_success == 3_911
    assert primary.control_n == 23_256
    assert primary.treatment_success == 4_949
    assert primary.treatment_n == 22_962
    assert math.isclose(primary.difference * 100, 4.7358351470, abs_tol=1e-9)
    assert math.isclose(primary.ci_low * 100, 4.0189317850, abs_tol=1e-9)
    assert math.isclose(primary.ci_high * 100, 5.4527385090, abs_tol=1e-9)


def test_all_four_metrics_match_the_committed_source_table() -> None:
    results = load_overall_metrics()
    assert [result.metric for result in results] == [
        "account_completed",
        "retention_7d",
        "complaint_7d",
        "first_deposit_7d",
    ]


def test_summary_is_english_first_and_includes_inference() -> None:
    rendered = format_metric(load_overall_metrics()[0])

    assert rendered.startswith("Account-opening completion:")
    assert "95% CI=[4.02, 5.45] pp" in rendered
    assert "p=" in rendered
    assert "supports staged rollout" in rendered


def test_metric_roles_make_the_multiplicity_policy_explicit() -> None:
    assert METRIC_ROLES["account_completed"] == "pre-specified primary outcome"
    assert METRIC_ROLES["complaint_7d"] == "harm guardrail"
    assert "not one confirmatory hypothesis family" in MULTIPLICITY_POLICY
    assert "Holm correction" in MULTIPLICITY_POLICY


@pytest.mark.parametrize(
    "counts, message",
    [
        ((1, 0, 1, 10), "control_n must be positive"),
        ((11, 10, 1, 10), "control_success must be between"),
        ((1, 10, -1, 10), "treatment_success must be between"),
    ],
)
def test_invalid_experiment_counts_fail_early(
    counts: tuple[int, int, int, int], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        calculate_proportion_effect(*counts)
