import pytest

from openeval.interface.cli import _evaluate_gates


def test_latency_gate_passes_when_within_limit() -> None:
    (
        _,
        passed,
        metric_results,
        operational_results,
        failures,
    ) = _evaluate_gates(
        overall_score=0.90,
        metric_scores={},
        gate_config={
            "max_latency_ms": 1000,
        },
        latency_ms=250,
    )

    assert passed is True
    assert metric_results == {}
    assert operational_results == {
        "latency": True,
    }
    assert failures == []


def test_latency_gate_fails_when_over_limit() -> None:
    (
        _,
        passed,
        metric_results,
        operational_results,
        failures,
    ) = _evaluate_gates(
        overall_score=0.90,
        metric_scores={},
        gate_config={
            "max_latency_ms": 1000,
        },
        latency_ms=1250,
    )

    assert passed is False
    assert metric_results == {}
    assert operational_results == {
        "latency": False,
    }
    assert failures == ["latency"]


def test_token_gate_passes_when_within_limit() -> None:
    (
        _,
        passed,
        metric_results,
        operational_results,
        failures,
    ) = _evaluate_gates(
        overall_score=0.90,
        metric_scores={},
        gate_config={
            "max_total_tokens": 5000,
        },
        total_tokens=4200,
    )

    assert passed is True
    assert metric_results == {}
    assert operational_results == {
        "tokens": True,
    }
    assert failures == []


def test_token_gate_fails_when_over_limit() -> None:
    (
        _,
        passed,
        metric_results,
        operational_results,
        failures,
    ) = _evaluate_gates(
        overall_score=0.90,
        metric_scores={},
        gate_config={
            "max_total_tokens": 5000,
        },
        total_tokens=5200,
    )

    assert passed is False
    assert metric_results == {}
    assert operational_results == {
        "tokens": False,
    }
    assert failures == ["tokens"]


def test_cost_gate_passes_when_within_limit() -> None:
    (
        _,
        passed,
        metric_results,
        operational_results,
        failures,
    ) = _evaluate_gates(
        overall_score=0.90,
        metric_scores={},
        gate_config={
            "max_cost_usd": 0.05,
        },
        combined_cost=0.03,
    )

    assert passed is True
    assert metric_results == {}
    assert operational_results == {
        "cost": True,
    }
    assert failures == []


def test_cost_gate_fails_when_over_limit() -> None:
    (
        _,
        passed,
        metric_results,
        operational_results,
        failures,
    ) = _evaluate_gates(
        overall_score=0.90,
        metric_scores={},
        gate_config={
            "max_cost_usd": 0.05,
        },
        combined_cost=0.08,
    )

    assert passed is False
    assert metric_results == {}
    assert operational_results == {
        "cost": False,
    }
    assert failures == ["cost"]


def test_cost_gate_fails_when_cost_is_unavailable() -> None:
    (
        _,
        passed,
        metric_results,
        operational_results,
        failures,
    ) = _evaluate_gates(
        overall_score=0.90,
        metric_scores={},
        gate_config={
            "max_cost_usd": 0.05,
        },
        combined_cost=None,
    )

    assert passed is False
    assert metric_results == {}
    assert operational_results == {
        "cost": False,
    }
    assert failures == ["cost"]


@pytest.mark.parametrize(
    ("gate_key", "value", "message"),
    [
        (
            "max_latency_ms",
            -1,
            "gate.max_latency_ms must be greater than or equal to 0",
        ),
        (
            "max_total_tokens",
            -1,
            "gate.max_total_tokens must be greater than or equal to 0",
        ),
        (
            "max_cost_usd",
            -1,
            "gate.max_cost_usd must be greater than or equal to 0",
        ),
    ],
)
def test_operational_gate_rejects_negative_limits(
    gate_key: str,
    value: int,
    message: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=message,
    ):
        _evaluate_gates(
            overall_score=0.90,
            metric_scores={},
            gate_config={
                gate_key: value,
            },
            latency_ms=100,
            total_tokens=100,
            combined_cost=0.01,
        )
