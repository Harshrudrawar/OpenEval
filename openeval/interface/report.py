from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from html import escape
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class TokenUsage:
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0


@dataclass(frozen=True)
class CostSummary:
    target_cost: float | None = None
    judge_cost: float | None = None
    combined_cost: float | None = None


def _format_latency(latency_ms: float) -> str:
    if latency_ms >= 1000:
        return f"{latency_ms / 1000:.1f}s"

    return f"{latency_ms:.0f} ms"


def _format_cost(cost: float | None) -> str:
    if cost is None:
        return "N/A"

    return f"${cost:.6f}"


def _format_limit(
    value: float | int | None,
    *,
    kind: str,
) -> str:
    if value is None:
        return "N/A"

    if kind == "latency":
        return f"{float(value):.0f} ms"

    if kind == "tokens":
        return f"{int(value):,}"

    if kind == "cost":
        return f"${float(value):.6f}"

    return str(value)


def _usage_cards(
    usage: TokenUsage,
    *,
    prefix: str,
) -> str:
    return f"""
      <div class="usage-item">
        <span class="label">{escape(prefix)} Input Tokens</span>
        <div class="usage-value">{usage.input_tokens:,}</div>
      </div>

      <div class="usage-item">
        <span class="label">{escape(prefix)} Output Tokens</span>
        <div class="usage-value">{usage.output_tokens:,}</div>
      </div>

      <div class="usage-item">
        <span class="label">{escape(prefix)} Total Tokens</span>
        <div class="usage-value">{usage.total_tokens:,}</div>
      </div>
    """


def _cost_cards(
    costs: CostSummary,
) -> str:
    return f"""
      <div class="usage-item">
        <span class="label">Target Cost</span>
        <div class="usage-value">
          {escape(_format_cost(costs.target_cost))}
        </div>
      </div>

      <div class="usage-item">
        <span class="label">Judge Cost</span>
        <div class="usage-value">
          {escape(_format_cost(costs.judge_cost))}
        </div>
      </div>

      <div class="usage-item">
        <span class="label">Combined Cost</span>
        <div class="usage-value">
          {escape(_format_cost(costs.combined_cost))}
        </div>
      </div>
    """


def _gate_status_card(
    name: str,
    passed: bool,
) -> str:
    status = "PASSED" if passed else "FAILED"
    status_class = "success" if passed else "danger"

    return f"""
      <div class="gate-item">
        <div class="gate-item-name">
          {escape(name)}
        </div>
        <div class="gate-item-status {status_class}">
          {status}
        </div>
      </div>
    """


def _build_metric_gate_cards(
    metric_gate_results: dict[str, bool],
) -> str:
    if not metric_gate_results:
        return """
          <div class="gate-empty">
            No per-metric gates configured.
          </div>
        """

    return "\n".join(
        _gate_status_card(
            metric_name,
            passed,
        )
        for metric_name, passed in metric_gate_results.items()
    )


def _build_operational_gate_cards(
    operational_gate_results: dict[str, bool],
    *,
    latency_ms: float,
    combined_usage: TokenUsage,
    costs: CostSummary,
    gate_config: dict[str, Any],
) -> str:
    if not operational_gate_results:
        return """
          <div class="gate-empty">
            No operational gates configured.
          </div>
        """

    cards: list[str] = []

    if "latency" in operational_gate_results:
        max_latency = gate_config.get("max_latency_ms")

        current = f"{latency_ms:.0f} ms"
        limit = _format_limit(
            max_latency,
            kind="latency",
        )

        passed = operational_gate_results["latency"]

        status = "PASSED" if passed else "FAILED"
        status_class = "success" if passed else "danger"

        cards.append(f"""
            <div class="gate-item operational-item">
              <div>
                <div class="gate-item-name">
                  Latency
                </div>
                <div class="gate-item-detail">
                  {escape(current)} / {escape(limit)}
                </div>
              </div>
              <div class="gate-item-status {status_class}">
                {status}
              </div>
            </div>
            """)

    if "tokens" in operational_gate_results:
        max_tokens = gate_config.get("max_total_tokens")

        current = f"{combined_usage.total_tokens:,}"
        limit = _format_limit(
            max_tokens,
            kind="tokens",
        )

        passed = operational_gate_results["tokens"]

        status = "PASSED" if passed else "FAILED"
        status_class = "success" if passed else "danger"

        cards.append(f"""
            <div class="gate-item operational-item">
              <div>
                <div class="gate-item-name">
                  Total Tokens
                </div>
                <div class="gate-item-detail">
                  {escape(current)} / {escape(limit)}
                </div>
              </div>
              <div class="gate-item-status {status_class}">
                {status}
              </div>
            </div>
            """)

    if "cost" in operational_gate_results:
        max_cost = gate_config.get("max_cost_usd")

        current = _format_cost(costs.combined_cost)

        limit = _format_limit(
            max_cost,
            kind="cost",
        )

        passed = operational_gate_results["cost"]

        status = "PASSED" if passed else "FAILED"
        status_class = "success" if passed else "danger"

        cards.append(f"""
            <div class="gate-item operational-item">
              <div>
                <div class="gate-item-name">
                  API Cost
                </div>
                <div class="gate-item-detail">
                  {escape(current)} / {escape(limit)}
                </div>
              </div>
              <div class="gate-item-status {status_class}">
                {status}
              </div>
            </div>
            """)

    return "\n".join(cards)


def _build_gate_failure_cards(
    gate_failures: list[str],
) -> str:
    if not gate_failures:
        return """
          <div class="gate-empty">
            No gate failures.
          </div>
        """

    return "\n".join(f"""
        <div class="failure-item">
          {escape(failure)}
        </div>
        """ for failure in gate_failures)


def build_run_report_html(
    *,
    evaluation_name: str,
    evaluation_id: str,
    run_id: str,
    dataset_version: str,
    prompt_version: str,
    provider: str,
    model: str,
    metric_scores: dict[str, float],
    judge_provider: str | None,
    judge_model: str | None,
    cases_count: int,
    case_results_count: int,
    overall_score: float,
    latency_ms: float,
    target_usage: TokenUsage,
    judge_usage: TokenUsage,
    combined_usage: TokenUsage,
    costs: CostSummary,
    gate_threshold: float | None,
    gate_passed: bool | None,
    metric_gate_results: dict[str, bool] | None = None,
    operational_gate_results: dict[str, bool] | None = None,
    gate_failures: list[str] | None = None,
    gate_config: dict[str, Any] | None = None,
    run_status: str = "completed",
    completed_cases_count: int | None = None,
    failed_cases_count: int | None = None,
    failed_cases: list[dict[str, str]] | None = None,
    metric_weights: dict[str, float] | None = None,
    regression_source: str | None = None,
    baseline_score: float | None = None,
    regression_delta: float | None = None,
    regression_passed: bool | None = None,
) -> str:
    metric_gate_results = metric_gate_results or {}
    operational_gate_results = operational_gate_results or {}
    gate_failures = gate_failures or []
    gate_config = gate_config or {}
    failed_cases = failed_cases or []
    metric_weights = metric_weights or {}

    if completed_cases_count is None:
        completed_cases_count = max(cases_count - len(failed_cases), 0)

    if failed_cases_count is None:
        failed_cases_count = len(failed_cases)

    generated_at = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")

    if gate_threshold is None:
        if gate_passed is None:
            gate_display = "Not configured"
            gate_class = "neutral"
        elif gate_passed:
            gate_display = "Passed"
            gate_class = "success"
        else:
            gate_display = "Failed"
            gate_class = "danger"
    elif gate_passed:
        gate_display = f"Passed ({gate_threshold:.2f})"
        gate_class = "success"
    else:
        gate_display = f"Failed ({gate_threshold:.2f})"
        gate_class = "danger"

    target_display = f"{provider}:{model}"
    latency_display = _format_latency(latency_ms)
    metric_names = list(metric_scores)

    if "llm_judge" in metric_names:
        judge_display = f"{judge_provider or 'unknown'}:" f"{judge_model or 'unknown'}"
    else:
        judge_display = "Not applicable"

    metrics_display = ", ".join(metric_names) if metric_names else "none"

    target_usage_cards = _usage_cards(
        target_usage,
        prefix="Target",
    )

    judge_usage_cards = _usage_cards(
        judge_usage,
        prefix="Judge",
    )

    combined_usage_cards = _usage_cards(
        combined_usage,
        prefix="Combined",
    )

    cost_cards = _cost_cards(costs)

    metric_gate_cards = _build_metric_gate_cards(metric_gate_results)

    operational_gate_cards = _build_operational_gate_cards(
        operational_gate_results,
        latency_ms=latency_ms,
        combined_usage=combined_usage,
        costs=costs,
        gate_config=gate_config,
    )

    gate_failure_cards = _build_gate_failure_cards(gate_failures)

    metric_weight_cards = "\n".join(f"""
      <div class="gate-item operational-item">
        <div>
          <div class="gate-item-name">
            {escape(metric_name)}
          </div>
          <div class="gate-item-detail">
            Score: {metric_scores.get(metric_name, 0.0):.2f}
          </div>
        </div>
        <div class="gate-item-status neutral">
          Weight: {weight:.2f}
        </div>
      </div>
    """ for metric_name, weight in metric_weights.items())

    if not metric_weight_cards:
        metric_weight_cards = (
            '<div class="gate-empty">No metric weights configured.</div>'
        )

    failed_case_cards = "\n".join(f"""
      <div class="failure-item">
        <strong>{escape(case.get("case_id", ""))}</strong>
        — {escape(case.get("error_type", "ExecutionError"))}:
        {escape(case.get("error_message", "Case execution failed"))}
      </div>
    """ for case in failed_cases)

    if not failed_case_cards:
        failed_case_cards = '<div class="gate-empty">No failed cases.</div>'

    if run_status == "completed":
        run_status_class = "success"
    elif run_status == "failed":
        run_status_class = "danger"
    else:
        run_status_class = "neutral"

    run_status_display = run_status.capitalize()

    if baseline_score is None:
        regression_display = "Not configured"
        regression_class = "neutral"
        regression_detail = "No baseline regression check was performed."
    else:
        regression_display = "Passed" if regression_passed else "Failed"
        regression_class = "success" if regression_passed else "danger"
        delta_text = (
            f"{regression_delta:+.2f}" if regression_delta is not None else "N/A"
        )
        regression_detail = (
            f"Baseline: {baseline_score:.2f} · "
            f"Current: {overall_score:.2f} · "
            f"Delta: {delta_text}"
        )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta
    name="viewport"
    content="width=device-width, initial-scale=1"
  />
  <title>OpenEval Evaluation Report</title>

  <style>
    :root {{
      --bg: #f6f8fc;
      --card: #ffffff;
      --text: #172033;
      --muted: #64748b;
      --border: #e2e8f0;
      --accent: #2563eb;
      --accent-soft: #eff6ff;
      --success: #16a34a;
      --success-soft: #f0fdf4;
      --danger: #dc2626;
      --danger-soft: #fef2f2;
      --neutral-soft: #f8fafc;
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      font-family:
        Inter,
        ui-sans-serif,
        system-ui,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;
      background: var(--bg);
      color: var(--text);
    }}

    .container {{
      max-width: 1080px;
      margin: 0 auto;
      padding: 36px 20px 60px;
    }}

    .hero {{
      background:
        radial-gradient(
          circle at top right,
          rgba(59, 130, 246, 0.45),
          transparent 34%
        ),
        linear-gradient(
          135deg,
          #0f172a 0%,
          #172554 100%
        );
      color: white;
      border-radius: 24px;
      padding: 32px;
      box-shadow:
        0 20px 55px
        rgba(15, 23, 42, 0.2);
      margin-bottom: 22px;
    }}

    .hero h1 {{
      margin: 0 0 10px;
      font-size: 34px;
      line-height: 1.1;
    }}

    .hero p {{
      margin: 0;
      color:
        rgba(255, 255, 255, 0.88);
      font-size: 14px;
    }}

    .subtle {{
      margin-top: 10px;
      color:
        rgba(255, 255, 255, 0.7);
      font-size: 13px;
    }}

    .badge {{
      display: inline-block;
      background:
        rgba(255, 255, 255, 0.12);
      color: white;
      border:
        1px solid
        rgba(255, 255, 255, 0.16);
      border-radius: 999px;
      padding: 6px 11px;
      font-size: 12px;
      font-weight: 600;
      margin-bottom: 16px;
    }}

    .summary {{
      display: grid;
      grid-template-columns:
        repeat(
          auto-fit,
          minmax(175px, 1fr)
        );
      gap: 16px;
      margin: 22px 0;
    }}

    .card {{
      background: var(--card);
      border:
        1px solid
        var(--border);
      border-radius: 18px;
      padding: 19px;
      box-shadow:
        0 10px 26px
        rgba(15, 23, 42, 0.05);
    }}

    .label {{
      display: block;
      color: var(--muted);
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.09em;
      margin-bottom: 9px;
    }}

    .value {{
      font-size: 23px;
      font-weight: 750;
      overflow-wrap: anywhere;
    }}

    .success {{
      color: var(--success);
    }}

    .danger {{
      color: var(--danger);
    }}

    .neutral {{
      color: var(--muted);
    }}

    .section {{
      margin-top: 22px;
    }}

    .section h2 {{
      margin: 0 0 13px;
      font-size: 18px;
    }}

    .meta {{
      display: grid;
      grid-template-columns:
        repeat(
          auto-fit,
          minmax(230px, 1fr)
        );
      gap: 12px;
    }}

    .meta-item {{
      background: var(--card);
      border:
        1px solid
        var(--border);
      border-radius: 16px;
      padding: 17px;
    }}

    .meta-key {{
      font-size: 11px;
      font-weight: 700;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.09em;
      margin-bottom: 8px;
    }}

    .meta-value {{
      font-weight: 650;
      overflow-wrap: anywhere;
    }}

    .usage {{
      margin-top: 22px;
      background: var(--neutral-soft);
      border:
        1px solid
        var(--border);
      border-radius: 18px;
      padding: 20px;
    }}

    .usage h2 {{
      margin: 0 0 16px;
      font-size: 18px;
    }}

    .usage-group {{
      margin-top: 16px;
    }}

    .usage-group:first-child {{
      margin-top: 0;
    }}

    .usage-group-title {{
      font-size: 12px;
      font-weight: 750;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 9px;
    }}

    .usage-grid {{
      display: grid;
      grid-template-columns:
        repeat(
          auto-fit,
          minmax(180px, 1fr)
        );
      gap: 12px;
    }}

    .usage-item {{
      background: var(--card);
      border:
        1px solid
        var(--border);
      border-radius: 14px;
      padding: 16px;
    }}

    .usage-value {{
      font-size: 22px;
      font-weight: 750;
    }}

    .judge {{
      margin-top: 22px;
      background: var(--accent-soft);
      border:
        1px solid
        #bfdbfe;
      border-radius: 18px;
      padding: 20px;
    }}

    .judge h2 {{
      margin: 0 0 14px;
      font-size: 18px;
    }}

    .judge-grid {{
      display: grid;
      grid-template-columns:
        repeat(
          auto-fit,
          minmax(200px, 1fr)
        );
      gap: 12px;
    }}

    .judge-item {{
      background:
        rgba(255, 255, 255, 0.72);
      border:
        1px solid
        rgba(37, 99, 235, 0.14);
      border-radius: 14px;
      padding: 14px;
    }}

    .gate-panel {{
      margin-top: 22px;
      border-radius: 18px;
      padding: 20px;
    }}

    .gate-panel.success {{
      background:
        var(--success-soft);
      border:
        1px solid
        #bbf7d0;
    }}

    .gate-panel.danger {{
      background:
        var(--danger-soft);
      border:
        1px solid
        #fecaca;
    }}

    .gate-panel.neutral {{
      background:
        var(--neutral-soft);
      border:
        1px solid
        var(--border);
    }}

    .gate-title {{
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.09em;
      margin-bottom: 7px;
    }}

    .gate-value {{
      font-size: 22px;
      font-weight: 750;
    }}

    .gate-section {{
      margin-top: 14px;
    }}

    .gate-section-title {{
      font-size: 12px;
      font-weight: 750;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--muted);
      margin-bottom: 9px;
    }}

    .gate-grid {{
      display: grid;
      grid-template-columns:
        repeat(
          auto-fit,
          minmax(220px, 1fr)
        );
      gap: 10px;
    }}

    .gate-item {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      background: var(--card);
      border:
        1px solid
        var(--border);
      border-radius: 14px;
      padding: 14px 15px;
    }}

    .operational-item {{
      align-items: flex-start;
    }}

    .gate-item-name {{
      font-weight: 700;
      overflow-wrap: anywhere;
    }}

    .gate-item-detail {{
      color: var(--muted);
      font-size: 12px;
      margin-top: 4px;
    }}

    .gate-item-status {{
      font-size: 11px;
      font-weight: 800;
      white-space: nowrap;
    }}

    .gate-empty {{
      color: var(--muted);
      font-size: 13px;
      background: var(--card);
      border:
        1px solid
        var(--border);
      border-radius: 14px;
      padding: 14px;
    }}

    .failure-panel {{
      margin-top: 14px;
      background:
        var(--danger-soft);
      border:
        1px solid
        #fecaca;
      border-radius: 14px;
      padding: 14px;
    }}

    .failure-item {{
      color:
        var(--danger);
      font-size: 13px;
      font-weight: 650;
      padding: 4px 0;
    }}

    .status-card {{
      margin-top: 22px;
      border-radius: 18px;
      padding: 20px;
      background: var(--card);
      border: 1px solid var(--border);
    }}

    .status-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
      margin-top: 12px;
    }}

    .regression-card {{
      margin-top: 22px;
      border-radius: 18px;
      padding: 20px;
      background: var(--card);
      border: 1px solid var(--border);
    }}

    .regression-value {{
      font-size: 22px;
      font-weight: 750;
    }}

    .footer {{
      margin-top: 26px;
      color: var(--muted);
      font-size: 13px;
      text-align: center;
    }}
  </style>
</head>

<body>
  <main class="container">

    <section class="hero">
      <div class="badge">
        OpenEval Evaluation Report
      </div>

      <h1>
        {escape(evaluation_name)}
      </h1>

      <p>
        Run ID: {escape(run_id)}
        · Evaluation ID:
        {escape(evaluation_id)}
      </p>

      <div class="subtle">
        Generated at {escape(generated_at)}
      </div>
    </section>

    <section class="summary">

      <div class="card">
        <span class="label">
          Overall Score
        </span>
        <div class="value">
          {overall_score:.2f}
        </div>
      </div>

      <div class="card">
        <span class="label">
          Target
        </span>
        <div class="value">
          {escape(target_display)}
        </div>
      </div>

      <div class="card">
        <span class="label">
          Latency
        </span>
        <div class="value">
          {escape(latency_display)}
        </div>
      </div>

      <div class="card">
        <span class="label">
          Cases
        </span>
        <div class="value">
          {cases_count}
        </div>
      </div>

      <div class="card">
        <span class="label">
          Metric Count
        </span>
        <div class="value">
          {len(metric_scores)}
        </div>
      </div>

      <div class="card">
        <span class="label">
          Combined Tokens
        </span>
        <div class="value">
          {combined_usage.total_tokens:,}
        </div>
      </div>

      <div class="card">
        <span class="label">
          Combined API Cost
        </span>
        <div class="value">
          {escape(
              _format_cost(
                  costs.combined_cost
              )
          )}
        </div>
      </div>

    </section>

    <section class="status-card">
      <div class="gate-section-title">Run Execution</div>
      <div class="status-grid">
        <div class="card">
          <span class="label">Run Status</span>
          <div class="value {run_status_class}">{escape(run_status_display)}</div>
        </div>
        <div class="card">
          <span class="label">Completed Cases</span>
          <div class="value">{completed_cases_count}</div>
        </div>
        <div class="card">
          <span class="label">Failed Cases</span>
          <div class="value">
            {'danger' if failed_cases_count else ''}
            {failed_cases_count}
          </div>
        </div>
      </div>
    </section>

    <section class="gate-panel {gate_class}">
      <div class="gate-title">
        Quality Gate
      </div>

      <div class="gate-value">
        {escape(gate_display)}
      </div>

      <div class="gate-section">
        <div class="gate-section-title">
          Metric Gates
        </div>

        <div class="gate-grid">
          {metric_gate_cards}
        </div>
      </div>

      <div class="gate-section">
        <div class="gate-section-title">
          Operational Gates
        </div>

        <div class="gate-grid">
          {operational_gate_cards}
        </div>
      </div>

      {
        f'''
        <div class="failure-panel">
          <div class="gate-section-title">
            Gate Failures
          </div>

          {gate_failure_cards}
        </div>
        '''
        if gate_failures
        else ""
      }

    </section>

    <section class="section">
      <h2>
        Metric Scores &amp; Weights
      </h2>

      <div class="gate-grid">
        {metric_weight_cards}
      </div>
    </section>

    <section class="section">
      <h2>
        Failed Cases
      </h2>

      <div class="failure-panel">
        {failed_case_cards}
      </div>
    </section>

    <section class="regression-card">
      <div class="gate-section-title">Regression</div>
      <div class="regression-value {regression_class}">
        {escape(regression_display)}
      </div>
      <div class="gate-item-detail">
        Source: {escape(regression_source or "none")} · {escape(regression_detail)}
      </div>
    </section>

    <section class="usage">
      <h2>
        Token Usage
      </h2>

      <div class="usage-group">
        <div class="usage-group-title">
          Target
        </div>

        <div class="usage-grid">
          {target_usage_cards}
        </div>
      </div>

      <div class="usage-group">
        <div class="usage-group-title">
          Judge
        </div>

        <div class="usage-grid">
          {judge_usage_cards}
        </div>
      </div>

      <div class="usage-group">
        <div class="usage-group-title">
          Combined
        </div>

        <div class="usage-grid">
          {combined_usage_cards}
        </div>
      </div>

      <div class="usage-group">
        <div class="usage-group-title">
          Estimated API Cost
        </div>

        <div class="usage-grid">
          {cost_cards}
        </div>
      </div>
    </section>

    <section class="section">
      <h2>
        Evaluation Details
      </h2>

      <div class="meta">

        <div class="meta-item">
          <div class="meta-key">
            Dataset Version
          </div>
          <div class="meta-value">
            {escape(dataset_version)}
          </div>
        </div>

        <div class="meta-item">
          <div class="meta-key">
            Prompt Version
          </div>
          <div class="meta-value">
            {escape(prompt_version)}
          </div>
        </div>

        <div class="meta-item">
          <div class="meta-key">
            Provider
          </div>
          <div class="meta-value">
            {escape(provider)}
          </div>
        </div>

        <div class="meta-item">
          <div class="meta-key">
            Model
          </div>
          <div class="meta-value">
            {escape(model)}
          </div>
        </div>

        <div class="meta-item">
          <div class="meta-key">
            Metrics
          </div>
          <div class="meta-value">
            {escape(metrics_display)}
          </div>
        </div>

        <div class="meta-item">
          <div class="meta-key">
            Case Results
          </div>
          <div class="meta-value">
            {case_results_count}
          </div>
        </div>

        <div class="meta-item">
          <div class="meta-key">
            Status
          </div>
          <div class="meta-value {run_status_class}">
            {escape(run_status_display)}
          </div>
        </div>

      </div>
    </section>

    <section class="judge">
      <h2>
        Evaluation Strategy
      </h2>

      <div class="judge-grid">

        <div class="judge-item">
          <div class="meta-key">
            Metric Set
          </div>

          <div class="meta-value">
            {escape(metrics_display)}
          </div>
        </div>

        <div class="judge-item">
          <div class="meta-key">
            Judge
          </div>

          <div class="meta-value">
            {escape(judge_display)}
          </div>
        </div>

      </div>
    </section>

    <div class="footer">
      Built with OpenEval ·
      Reproducible AI quality evaluation
    </div>

  </main>
</body>
</html>
"""


def build_comparison_report_html(
    *,
    evaluation_name: str,
    evaluation_id: str,
    dataset_version: str,
    prompt_version: str,
    left_name: str,
    right_name: str,
    left_accuracy: float,
    right_accuracy: float,
    winner: str,
    margin: float,
) -> str:
    generated_at = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta
    name="viewport"
    content="width=device-width, initial-scale=1"
  />
  <title>
    OpenEval Comparison Report
  </title>

  <style>
    :root {{
      --bg: #f6f8fc;
      --card: #ffffff;
      --text: #172033;
      --muted: #64748b;
      --border: #e2e8f0;
      --success: #16a34a;
      --accent: #2563eb;
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      font-family:
        Inter,
        ui-sans-serif,
        system-ui,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;
      background: var(--bg);
      color: var(--text);
    }}

    .container {{
      max-width: 1040px;
      margin: 0 auto;
      padding: 32px 20px 56px;
    }}

    .hero {{
      background:
        linear-gradient(
          135deg,
          #0f172a 0%,
          #1e3a8a 100%
        );
      color: white;
      border-radius: 24px;
      padding: 28px;
      box-shadow:
        0 18px 50px
        rgba(15, 23, 42, 0.18);
      margin-bottom: 20px;
    }}

    .hero h1 {{
      margin: 0 0 8px;
      font-size: 32px;
      line-height: 1.1;
    }}

    .hero p {{
      margin: 0;
      color:
        rgba(255, 255, 255, 0.88);
      font-size: 15px;
    }}

    .subtle {{
      margin-top: 10px;
      color:
        rgba(255, 255, 255, 0.75);
      font-size: 13px;
    }}

    .grid {{
      display: grid;
      grid-template-columns:
        repeat(
          auto-fit,
          minmax(220px, 1fr)
        );
      gap: 16px;
      margin: 20px 0;
    }}

    .card {{
      background: var(--card);
      border:
        1px solid
        var(--border);
      border-radius: 18px;
      padding: 18px;
      box-shadow:
        0 10px 26px
        rgba(15, 23, 42, 0.05);
    }}

    .label {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 8px;
    }}

    .value {{
      font-size: 22px;
      font-weight: 700;
    }}

    .winner {{
      color: var(--success);
    }}

    .footer {{
      margin-top: 22px;
      color: var(--muted);
      font-size: 13px;
      text-align: center;
    }}

    .badge {{
      display: inline-block;
      background:
        rgba(255, 255, 255, 0.12);
      color: white;
      border:
        1px solid
        rgba(255, 255, 255, 0.15);
      border-radius: 999px;
      padding: 6px 10px;
      font-size: 12px;
      margin-bottom: 14px;
    }}
  </style>
</head>

<body>
  <main class="container">

    <section class="hero">
      <div class="badge">
        OpenEval Comparison Report
      </div>

      <h1>
        {escape(evaluation_name)}
      </h1>

      <p>
        Evaluation ID:
        {escape(evaluation_id)}
      </p>

      <div class="subtle">
        Generated at {escape(generated_at)}
      </div>
    </section>

    <section class="grid">

      <div class="card">
        <span class="label">
          Left Provider
        </span>

        <div class="value">
          {escape(left_name)}
        </div>
      </div>

      <div class="card">
        <span class="label">
          Right Provider
        </span>

        <div class="value">
          {escape(right_name)}
        </div>
      </div>

      <div class="card">
        <span class="label">
          Winner
        </span>

        <div class="value winner">
          {escape(winner)}
        </div>
      </div>

      <div class="card">
        <span class="label">
          Margin
        </span>

        <div class="value">
          {margin:.2f}
        </div>
      </div>

    </section>

    <section class="grid">

      <div class="card">
        <span class="label">
          Left Accuracy
        </span>

        <div class="value">
          {left_accuracy:.2f}
        </div>
      </div>

      <div class="card">
        <span class="label">
          Right Accuracy
        </span>

        <div class="value">
          {right_accuracy:.2f}
        </div>
      </div>

      <div class="card">
        <span class="label">
          Dataset Version
        </span>

        <div class="value">
          {escape(dataset_version)}
        </div>
      </div>

      <div class="card">
        <span class="label">
          Prompt Version
        </span>

        <div class="value">
          {escape(prompt_version)}
        </div>
      </div>

    </section>

    <div class="footer">
      Built with OpenEval
    </div>

  </main>
</body>
</html>
"""


def write_run_report(
    output_dir: str | Path,
    *,
    evaluation_name: str,
    evaluation_id: str,
    run_id: str,
    dataset_version: str,
    prompt_version: str,
    provider: str,
    model: str,
    metric_scores: dict[str, float],
    judge_provider: str | None,
    judge_model: str | None,
    cases_count: int,
    case_results_count: int,
    overall_score: float,
    latency_ms: float,
    target_usage: TokenUsage,
    judge_usage: TokenUsage,
    combined_usage: TokenUsage,
    costs: CostSummary,
    gate_threshold: float | None,
    gate_passed: bool | None,
    metric_gate_results: dict[str, bool] | None = None,
    operational_gate_results: dict[str, bool] | None = None,
    gate_failures: list[str] | None = None,
    gate_config: dict[str, Any] | None = None,
    run_status: str = "completed",
    completed_cases_count: int | None = None,
    failed_cases_count: int | None = None,
    failed_cases: list[dict[str, str]] | None = None,
    metric_weights: dict[str, float] | None = None,
    regression_source: str | None = None,
    baseline_score: float | None = None,
    regression_delta: float | None = None,
    regression_passed: bool | None = None,
) -> Path:
    out_dir = Path(output_dir)
    out_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    report_path = out_dir / f"{run_id}.html"

    report_path.write_text(
        build_run_report_html(
            evaluation_name=evaluation_name,
            evaluation_id=evaluation_id,
            run_id=run_id,
            dataset_version=dataset_version,
            prompt_version=prompt_version,
            provider=provider,
            model=model,
            metric_scores=metric_scores,
            judge_provider=judge_provider,
            judge_model=judge_model,
            cases_count=cases_count,
            case_results_count=case_results_count,
            overall_score=overall_score,
            latency_ms=latency_ms,
            target_usage=target_usage,
            judge_usage=judge_usage,
            combined_usage=combined_usage,
            costs=costs,
            gate_threshold=gate_threshold,
            gate_passed=gate_passed,
            metric_gate_results=metric_gate_results,
            operational_gate_results=(operational_gate_results),
            gate_failures=gate_failures,
            gate_config=gate_config,
            run_status=run_status,
            completed_cases_count=completed_cases_count,
            failed_cases_count=failed_cases_count,
            failed_cases=failed_cases,
            metric_weights=metric_weights,
            regression_source=regression_source,
            baseline_score=baseline_score,
            regression_delta=regression_delta,
            regression_passed=regression_passed,
        ),
        encoding="utf-8",
    )

    return report_path


def write_comparison_report(
    output_dir: str | Path,
    *,
    evaluation_name: str,
    evaluation_id: str,
    dataset_version: str,
    prompt_version: str,
    left_name: str,
    right_name: str,
    left_accuracy: float,
    right_accuracy: float,
    winner: str,
    margin: float,
) -> Path:
    out_dir = Path(output_dir)
    out_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    report_path = out_dir / f"comparison-{evaluation_id}.html"

    report_path.write_text(
        build_comparison_report_html(
            evaluation_name=evaluation_name,
            evaluation_id=evaluation_id,
            dataset_version=dataset_version,
            prompt_version=prompt_version,
            left_name=left_name,
            right_name=right_name,
            left_accuracy=left_accuracy,
            right_accuracy=right_accuracy,
            winner=winner,
            margin=margin,
        ),
        encoding="utf-8",
    )

    return report_path


RUN_HISTORY_PATH = Path("reports") / "run-history.jsonl"


def append_run_history(
    record: dict[str, Any],
    history_path: str | Path = RUN_HISTORY_PATH,
) -> Path:
    path = Path(history_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "a",
        encoding="utf-8",
    ) as handle:
        handle.write(
            json.dumps(
                record,
                ensure_ascii=False,
            )
            + "\n"
        )

    return path
