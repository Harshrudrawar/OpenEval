from __future__ import annotations

from datetime import UTC, datetime
from html import escape
from pathlib import Path


def build_run_report_html(
    *,
    evaluation_name: str,
    evaluation_id: str,
    run_id: str,
    dataset_version: str,
    prompt_version: str,
    provider: str,
    model: str,
    cases_count: int,
    case_results_count: int,
    accuracy: float,
    latency_ms: float,
    gate_threshold: float | None,
    gate_passed: bool | None,
) -> str:
    generated_at = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")

    if gate_threshold is None:
        gate_display = "Not configured"
        gate_color = "var(--muted)"
    else:
        if gate_passed:
            gate_display = f"Passed ({gate_threshold:.2f})"
            gate_color = "var(--success)"
        else:
            gate_display = f"Failed ({gate_threshold:.2f})"
            gate_color = "var(--danger)"

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>OpenEval Run Report</title>
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
      --danger: #dc2626;
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system,
        BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--text);
    }}

    .container {{
      max-width: 1040px;
      margin: 0 auto;
      padding: 32px 20px 56px;
    }}

    .hero {{
      background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
      color: white;
      border-radius: 24px;
      padding: 28px;
      box-shadow: 0 18px 50px rgba(15, 23, 42, 0.18);
      margin-bottom: 20px;
    }}

    .hero h1 {{
      margin: 0 0 8px;
      font-size: 32px;
      line-height: 1.1;
    }}

    .hero p {{
      margin: 0;
      color: rgba(255, 255, 255, 0.88);
      font-size: 15px;
    }}

    .subtle {{
      margin-top: 10px;
      color: rgba(255, 255, 255, 0.75);
      font-size: 13px;
    }}

    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
      gap: 16px;
      margin: 20px 0;
    }}

    .card {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 18px;
      box-shadow: 0 10px 26px rgba(15, 23, 42, 0.05);
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

    .section {{
      margin-top: 18px;
    }}

    .section h2 {{
      margin: 0 0 12px;
      font-size: 18px;
    }}

    .meta {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 12px;
    }}

    .meta-item {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 16px;
    }}

    .meta-key {{
      font-size: 12px;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 8px;
    }}

    .meta-value {{
      font-weight: 600;
      overflow-wrap: anywhere;
    }}

    .footer {{
      margin-top: 22px;
      color: var(--muted);
      font-size: 13px;
      text-align: center;
    }}

    .badge {{
      display: inline-block;
      background: rgba(255, 255, 255, 0.12);
      color: white;
      border: 1px solid rgba(255, 255, 255, 0.15);
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
      <div class="badge">OpenEval Run Report</div>
      <h1>{escape(evaluation_name)}</h1>
      <p>Run ID: {escape(run_id)} · Evaluation ID: {escape(evaluation_id)}</p>
      <div class="subtle">Generated at {escape(generated_at)}</div>
    </section>

    <section class="grid">
      <div class="card">
        <span class="label">Accuracy</span>
        <div class="value">{accuracy:.2f}</div>
      </div>
      <div class="card">
        <span class="label">Latency</span>
        <div class="value">{latency_ms:.0f} ms</div>
      </div>
      <div class="card">
        <span class="label">Cases Loaded</span>
        <div class="value">{cases_count}</div>
      </div>
      <div class="card">
        <span class="label">Case Results</span>
        <div class="value">{case_results_count}</div>
      </div>
      <div class="card">
        <span class="label">Quality Gate</span>
        <div class="value" style="color: {gate_color};">{escape(gate_display)}</div>
      </div>
    </section>

    <section class="section">
      <h2>Evaluation Details</h2>
      <div class="meta">
        <div class="meta-item">
          <div class="meta-key">Dataset Version</div>
          <div class="meta-value">{escape(dataset_version)}</div>
        </div>
        <div class="meta-item">
          <div class="meta-key">Prompt Version</div>
          <div class="meta-value">{escape(prompt_version)}</div>
        </div>
        <div class="meta-item">
          <div class="meta-key">Provider</div>
          <div class="meta-value">{escape(provider)}</div>
        </div>
        <div class="meta-item">
          <div class="meta-key">Model</div>
          <div class="meta-value">{escape(model)}</div>
        </div>
        <div class="meta-item">
          <div class="meta-key">Status</div>
          <div class="meta-value" style="color: var(--success);">Completed</div>
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
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>OpenEval Comparison Report</title>
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
      font-family: Inter, ui-sans-serif, system-ui, -apple-system,
        BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--text);
    }}

    .container {{
      max-width: 1040px;
      margin: 0 auto;
      padding: 32px 20px 56px;
    }}

    .hero {{
      background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
      color: white;
      border-radius: 24px;
      padding: 28px;
      box-shadow: 0 18px 50px rgba(15, 23, 42, 0.18);
      margin-bottom: 20px;
    }}

    .hero h1 {{
      margin: 0 0 8px;
      font-size: 32px;
      line-height: 1.1;
    }}

    .hero p {{
      margin: 0;
      color: rgba(255, 255, 255, 0.88);
      font-size: 15px;
    }}

    .subtle {{
      margin-top: 10px;
      color: rgba(255, 255, 255, 0.75);
      font-size: 13px;
    }}

    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;
      margin: 20px 0;
    }}

    .card {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 18px;
      box-shadow: 0 10px 26px rgba(15, 23, 42, 0.05);
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

    .meta {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 12px;
      margin-top: 18px;
    }}

    .meta-item {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 16px;
    }}

    .meta-key {{
      font-size: 12px;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 8px;
    }}

    .meta-value {{
      font-weight: 600;
      overflow-wrap: anywhere;
    }}

    .badge {{
      display: inline-block;
      background: rgba(255, 255, 255, 0.12);
      color: white;
      border: 1px solid rgba(255, 255, 255, 0.15);
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
      <div class="badge">OpenEval Comparison Report</div>
      <h1>{escape(evaluation_name)}</h1>
      <p>Evaluation ID: {escape(evaluation_id)}</p>
      <div class="subtle">Generated at {escape(generated_at)}</div>
    </section>

    <section class="grid">
      <div class="card">
        <span class="label">Left Provider</span>
        <div class="value">{escape(left_name)}</div>
      </div>
      <div class="card">
        <span class="label">Right Provider</span>
        <div class="value">{escape(right_name)}</div>
      </div>
      <div class="card">
        <span class="label">Winner</span>
        <div class="value winner">{escape(winner)}</div>
      </div>
      <div class="card">
        <span class="label">Margin</span>
        <div class="value">{margin:.2f}</div>
      </div>
    </section>

    <section class="grid">
      <div class="card">
        <span class="label">Left Accuracy</span>
        <div class="value">{left_accuracy:.2f}</div>
      </div>
      <div class="card">
        <span class="label">Right Accuracy</span>
        <div class="value">{right_accuracy:.2f}</div>
      </div>
      <div class="card">
        <span class="label">Dataset Version</span>
        <div class="value">{escape(dataset_version)}</div>
      </div>
      <div class="card">
        <span class="label">Prompt Version</span>
        <div class="value">{escape(prompt_version)}</div>
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
    cases_count: int,
    case_results_count: int,
    accuracy: float,
    latency_ms: float,
    gate_threshold: float | None,
    gate_passed: bool | None,
) -> Path:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

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
            cases_count=cases_count,
            case_results_count=case_results_count,
            accuracy=accuracy,
            latency_ms=latency_ms,
            gate_threshold=gate_threshold,
            gate_passed=gate_passed,
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
    out_dir.mkdir(parents=True, exist_ok=True)

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
