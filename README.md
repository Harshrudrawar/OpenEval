<div align="center">

# 🚀 OpenEval

### Open-Source AI Evaluation & Quality Platform for LLM Applications

**Evaluate models • Compare providers • Judge responses • Detect regressions • Enforce AI quality**

<br>

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![CI](https://img.shields.io/github/actions/workflow/status/Harshrudrawar/OpenEval/ci.yml?branch=main&style=for-the-badge&label=CI)](https://github.com/Harshrudrawar/OpenEval/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-Apache%202.0-green?style=for-the-badge)](LICENSE)
![Version](https://img.shields.io/badge/version-1.0.0-blue?style=for-the-badge)

<br>

**Building reproducible, comparable, and continuously evaluated AI systems.**

</div>

---

## 💡 Why OpenEval?

Traditional software engineering has:

**Unit Tests → Integration Tests → CI/CD → Quality Gates**

AI applications need the same engineering discipline.

LLM systems are probabilistic. Prompt changes, model upgrades, provider changes,
and application updates can improve one behavior while silently degrading another.

OpenEval provides a structured evaluation workflow for LLM applications so
developers can:

- run reproducible evaluations from versioned configuration
- score model outputs with multiple metrics
- combine metrics using configurable weights
- use LLMs as semantic evaluation judges
- compare models and providers
- enforce overall and per-metric quality thresholds
- enforce latency, token, and API-cost budgets
- detect regressions against explicit or historical baselines
- survive individual case execution failures
- track token usage and estimated API cost
- generate rich HTML reports
- emit machine-readable JSON
- maintain persistent evaluation history
- integrate AI quality checks directly into CI/CD

Instead of asking:

> **"Does this model seem better?"**

OpenEval moves toward answering:

> **"Did AI quality improve, regress, or violate the quality and operational
> requirements we defined?"**

---

# ✨ OpenEval v1.0 Capabilities

| Capability | Status |
| --- | :---: |
| YAML-driven evaluations | ✅ |
| CSV dataset loading | ✅ |
| Automatic case generation | ✅ |
| Configuration validation | ✅ |
| Mock execution | ✅ |
| Local Ollama execution | ✅ |
| OpenAI execution | ✅ |
| Provider-based execution architecture | ✅ |
| Exact-match accuracy | ✅ |
| Short-answer containment scoring | ✅ |
| LLM-as-a-Judge with Ollama | ✅ |
| Multi-metric evaluation | ✅ |
| Weighted metric scoring | ✅ |
| Overall quality gates | ✅ |
| Per-metric quality gates | ✅ |
| Latency gates | ✅ |
| Token-budget gates | ✅ |
| API-cost gates | ✅ |
| Token usage tracking | ✅ |
| Estimated API-cost tracking | ✅ |
| Run lifecycle tracking | ✅ |
| Case-level failure resilience | ✅ |
| Explicit baselines | ✅ |
| Historical baselines | ✅ |
| Regression detection | ✅ |
| Provider/model comparison | ✅ |
| Persistent run history | ✅ |
| Persistent comparison history | ✅ |
| Rich HTML run reports | ✅ |
| HTML comparison reports | ✅ |
| Machine-readable JSON output | ✅ |
| CI-compatible exit codes | ✅ |
| GitHub Actions CI | ✅ |
| Reusable OpenEval GitHub Action | ✅ |

---

# ⚡ Quick Start

## 1. Clone OpenEval

```bash
git clone https://github.com/Harshrudrawar/OpenEval.git
cd OpenEval
```

## 2. Create a virtual environment

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
python -m venv .venv
source .venv/bin/activate
```

## 3. Install

For normal usage:

```bash
pip install -e .
```

For development:

```bash
pip install -e ".[dev]"
```

Verify the installation:

```bash
openeval --version
```

Expected:

```text
openeval 1.0.0
```

## 4. Validate an evaluation

```bash
openeval validate examples/weighted-metrics/evaluation.yaml
```

Example:

```text
✔ Configuration is valid
Evaluation: Weighted Metrics Demo
Dataset: dataset-v1
Prompt: prompt-v1
Metrics: accuracy, contains
```

## 5. Run an evaluation

```bash
openeval run examples/weighted-metrics/evaluation.yaml
```

Example:

```text
✔ Evaluation created successfully

Name: Weighted Metrics Demo
Dataset Version: dataset-v1
Prompt Version: prompt-v1
Metrics: 2

Loaded 3 cases
Created 3 case results
Completed Cases: 3
Failed Cases: 0

Overall Score: 1.00
Metric Scores:
  accuracy: 1.00 (weight: 0.25)
  contains: 1.00 (weight: 0.75)

Quality Gate: PASSED

Run execution completed
Run ID: <run-id>
Run Status: completed

Report written to: reports/<run-id>.html
History written to: reports/run-history.jsonl
```

The module form remains available:

```bash
python -m openeval.interface.cli run examples/weighted-metrics/evaluation.yaml
```

---

# ⚙️ Evaluation Configuration

OpenEval evaluations are defined using YAML.

A configuration can describe the dataset, prompt version, execution target,
metrics, quality gates, operational limits, judge configuration, and regression
policy.

Example:

```yaml
name: Production QA Evaluation

dataset:
  version: dataset-v1
  path: examples/weighted-metrics/dataset.csv

prompt:
  version: prompt-v1

target:
  provider: mock

metrics:
  - name: accuracy
    weight: 0.25
  - name: contains
    weight: 0.75

gate:
  overall: 0.80

  metrics:
    accuracy: 0.80
    contains: 0.90

  max_latency_ms: 30000
  max_total_tokens: 5000
  max_cost_usd: 0.05
```

Conceptually:

```text
Dataset Version
      +
Prompt Version
      +
Target Provider / Model
      +
Metric Set + Weights
      +
Quality Requirements
      +
Operational Budgets
      |
      v
Reproducible Evaluation Contract
```

Before executing a configuration, validate it:

```bash
openeval validate evaluation.yaml
```

Validation catches configuration problems such as malformed structures and
metric gates that reference metrics not present in the configured metric set.

---

# 🧠 Multi-Metric & Weighted Evaluation

Real AI quality rarely fits into one metric.

OpenEval can score the same model output using multiple independent evaluation
strategies.

```yaml
metrics:
  - name: accuracy
    weight: 0.25
  - name: contains
    weight: 0.75
```

The target executes once. Its outputs are then evaluated by every configured
metric plugin:

```text
                    Target
                      |
                      v
                 Execute Cases
                      |
                      v
                  Case Results
                      |
              +-------+-------+
              |               |
              v               v
          accuracy         contains
              |               |
              v               v
             0.80            1.00
              |               |
              +-------+-------+
                      |
                      v
              Weighted Overall
                      |
                      v
                 Quality Gate
```

The overall score is:

```text
Overall Score =
    sum(metric_score × metric_weight)
    ---------------------------------
            sum(metric_weight)
```

For example:

```text
accuracy = 0.80 × 0.25
contains = 1.00 × 0.75

Overall Score = 0.95
```

This allows teams to represent which aspects of model behavior matter most for
a particular evaluation.

---

# 📏 Evaluation Metrics

OpenEval v1.0 provides three metric strategies.

## Exact-Match Accuracy

Useful when the generated result should structurally match the expected output.

```yaml
metrics:
  - accuracy
```

String values are normalized for casing and surrounding whitespace.

## Short-Answer Containment

Useful when an LLM produces additional natural language around a correct short
answer.

```text
Expected:
Paris

Actual:
"The capital of France is Paris."

Score:
1.0
```

Configure with:

```yaml
metrics:
  - contains
```

## LLM-as-a-Judge

Useful when semantic correctness matters more than exact wording.

```yaml
metrics:
  - llm_judge

judge:
  provider: ollama
  model: llama3
```

The judge receives the expected and actual outputs and returns a structured
correct/incorrect decision.

The judge is intentionally separate from the target being evaluated:

```text
Target Model
    |
    v
Actual Output
    |
    +-------------------+
                        |
Expected Output --------+
                        |
                        v
                    LLM Judge
                        |
                        v
                    0.0 / 1.0
```

This allows one model to evaluate another.

---

# 🔌 Execution Providers

OpenEval separates target execution from evaluation logic.

| Provider | Status | Typical Use |
| --- | :---: | --- |
| **Mock** | ✅ | Deterministic tests and CI |
| **Ollama** | ✅ | Local LLM execution |
| **OpenAI** | ✅ | Cloud model execution |
| **Anthropic** | 🔜 | Future |
| **Gemini** | 🔜 | Future |

## Mock

```yaml
target:
  provider: mock
```

Useful for deterministic examples, development, and CI.

## Ollama

```yaml
target:
  provider: ollama
  model: llama3
```

The default Ollama API endpoint is local.

## OpenAI

```yaml
target:
  provider: openai
  model: gpt-4o
```

Authentication secrets should be supplied through environment variables rather
than committed to evaluation YAML.

---

# 🛡️ Quality Gates

Evaluation should do more than produce scores.

OpenEval can convert evaluation results into CI-enforceable decisions.

## Overall Gate

```yaml
gate:
  overall: 0.80
```

If the weighted overall score falls below `0.80`, the quality gate fails.

## Per-Metric Gates

Different behaviors can have independent requirements:

```yaml
gate:
  overall: 0.80

  metrics:
    accuracy: 0.75
    contains: 0.90
```

Example:

```text
Quality Gate: FAILED

Metric Gates:
  accuracy: PASSED
  contains: FAILED

Gate Failures:
  metric:contains
```

This prevents a strong metric from hiding unacceptable performance in another
metric.

---

# ⚙️ Operational Gates

AI quality is not only about correctness.

Production systems also have operational constraints.

OpenEval can enforce:

```yaml
gate:
  max_latency_ms: 30000
  max_total_tokens: 5000
  max_cost_usd: 0.05
```

Example:

```text
Operational Gates:
  Latency: PASSED (24 / 30000 ms)
  Total Tokens: PASSED (1200 / 5,000)
  API Cost: PASSED ($0.012500 / $0.050000)
```

An operational failure contributes to the overall gate decision.

If a configured cost gate cannot be evaluated because pricing is unavailable,
OpenEval handles the gate conservatively rather than silently passing it.

---

# 🪙 Token Usage & Estimated API Cost

OpenEval tracks target and judge usage separately.

```text
Usage
Target
  Input Tokens: 1,200
  Output Tokens: 300
  Total Tokens: 1,500

Judge
  Input Tokens: 800
  Output Tokens: 200
  Total Tokens: 1,000

Combined
  Input Tokens: 2,000
  Output Tokens: 500
  Total Tokens: 2,500
```

When pricing is known, OpenEval also estimates API cost:

```text
Estimated API Cost
Target: $0.006000
Judge: $0.004000
Combined: $0.010000
```

When pricing is unavailable, the value is represented as `N/A` in
human-readable output and `null` in JSON.

---

# 🛟 Failure Resilience & Run Lifecycle

A single provider failure should not erase the rest of an evaluation.

OpenEval captures case-level execution failures and continues executing the
remaining cases.

```text
3 Cases

Case 1 -> completed
Case 2 -> failed
Case 3 -> completed
```

Failed cases preserve structured failure information such as:

```text
case_id
error_type
error_message
```

Failed cases are excluded from metric scoring rather than being converted into
artificial quality scores.

The run lifecycle is:

```text
created
   |
   v
running
   |
   +-------> completed
   |
   +-------> failed
```

A run becomes `failed` when case execution failures occur.

This is distinct from a quality-gate failure.

For example:

```text
Run Status: completed
Quality Gate: FAILED
```

means the evaluation executed successfully, but the resulting model behavior
did not satisfy the configured requirements.

---

# 📉 Regression Detection

A model can pass a minimum quality threshold while still performing worse than
a previous version.

OpenEval supports regression checks to detect this.

```yaml
regression:
  max_drop: 0.05
```

## Explicit Baseline

```yaml
baseline:
  provider: mock
  model: baseline

regression:
  max_drop: 0.05
```

Example:

```text
Baseline Regression Check

Baseline (mock:baseline): 1.00
Current  (ollama:llama3): 0.67
Delta: -0.33
Result: REGRESSED

Allowed Drop: 0.05
Regression Gate: FAILED
```

---

# 🕘 Historical Baselines

OpenEval can also use a previous compatible successful run as the baseline.

```yaml
baseline:
  source: history

regression:
  max_drop: 0.05
```

Historical baseline matching considers evaluation context including:

- evaluation name
- dataset version
- prompt version
- metric configuration
- provider
- model

Example:

```text
Historical Baseline Check

Baseline (mock:unknown): 1.00
Current  (mock:unknown): 1.00
Delta: +0.00
Result: UNCHANGED

Allowed Drop: 0.05
Regression Gate: PASSED
```

---

# 🔀 Compare Models & Providers

OpenEval can run the same evaluation contract against two execution targets.

```bash
openeval compare examples/basic/evaluation.yaml \
  --left-provider ollama \
  --right-provider mock
```

Example:

```text
✔ Comparison completed successfully

Dataset Version: dataset-v1
Prompt Version: prompt-v1

Left (ollama:llama3): 0.67
Right (mock:unknown): 1.00

Winner: mock:unknown
Margin: 0.33
```

Comparison reports are written under `reports/`.

---

# 🤖 Machine-Readable Output

OpenEval can emit structured JSON for automation and CI tooling.

## Print JSON

```bash
openeval run examples/weighted-metrics/evaluation.yaml --json
```

Example:

```json
{
  "schema_version": "1",
  "run_id": "<run-id>",
  "evaluation_name": "Weighted Metrics Demo",
  "status": "completed",
  "provider": "mock",
  "model": "unknown",
  "overall_score": 1.0,
  "metrics": {
    "accuracy": 1.0,
    "contains": 1.0
  },
  "cases": {
    "total": 3,
    "completed": 3,
    "failed": 0
  },
  "estimated_cost_usd": null,
  "gates": {
    "passed": true,
    "metric_results": {},
    "operational_results": {},
    "failures": []
  },
  "failed_cases": []
}
```

`--json` prints machine-readable output without the normal human-oriented run
summary.

## Write JSON to Disk

```bash
openeval run examples/weighted-metrics/evaluation.yaml \
  --output reports/latest.json
```

This writes the structured result to the requested path while retaining the
normal CLI output.

---

# 🗂️ Evaluation History

OpenEval stores run and comparison history in:

```text
reports/run-history.jsonl
```

View recent history:

```bash
openeval history
```

Filter to runs:

```bash
openeval history --kind run
```

Filter to comparisons:

```bash
openeval history --kind comparison
```

History records preserve information such as:

- evaluation and run identifiers
- provider and model
- metric names, weights, and scores
- run lifecycle status
- completed and failed case counts
- failed-case details
- target, judge, and combined token usage
- estimated API costs
- gate results and failure reasons
- baseline information
- regression delta and result

Historical runs can therefore serve both as an audit trail and as regression
baselines.

---

# 📊 HTML Reports

OpenEval generates standalone HTML reports for evaluation runs.

Run reports include:

- overall score
- individual metric scores
- metric weights
- run lifecycle status
- completed and failed case counts
- failed-case details
- target provider and model
- judge provider and model when applicable
- dataset and prompt versions
- latency
- token usage
- estimated API costs
- overall quality-gate result
- per-metric gates
- operational gates
- gate failure reasons
- regression information
- evaluation and run identifiers

Reports are written to:

```text
reports/
```

Comparison runs generate dedicated HTML comparison reports.

Generated reports are intended to be runtime artifacts and should not normally
be committed to Git.

---

# ⚙️ CI/CD Integration

OpenEval uses process exit codes to make AI evaluation enforceable in CI.

```text
Evaluation
    |
    v
Execution
    |
    +---- execution failed ----> exit 1
    |
    v
Quality Gates
    |
    +---- failed -------------> exit 1
    |
    v
Regression Gate
    |
    +---- failed -------------> exit 1
    |
    v
PASS
    |
    v
exit 0
```

This allows a pull request or deployment pipeline to block when AI quality
regresses or violates operational requirements.

---

# ⚙️ GitHub Actions

The OpenEval repository validates itself using:

```text
Ruff
  |
  v
Black
  |
  v
MyPy
  |
  v
Pytest
  |
  v
OpenEval Quality Check
  |
  v
Evaluation Reports
```

This means OpenEval dogfoods its own evaluation system as part of repository CI.

---

# 🧩 Reusable OpenEval GitHub Action

OpenEval can also be consumed from another GitHub repository.

```yaml
- uses: Harshrudrawar/OpenEval/.github/actions/openeval@v1
  with:
    config: examples/basic/evaluation.yaml
```

Conceptually:

```text
Pull Request
     |
     v
GitHub Actions
     |
     v
OpenEval
     |
     v
Evaluation
     |
     v
Quality + Operational + Regression Gates
        /                  \
      PASS                 FAIL
       |                     |
       v                     v
     Merge                  Block
```

The goal is to make AI quality checks behave like normal software quality
checks.

---

# 🔄 Evaluation Pipeline

```text
evaluation.yaml
      |
      v
Validate Configuration
      |
      v
Load Dataset
      |
      v
Create Cases
      |
      v
Create Evaluation
      |
      v
Create Run
      |
      v
Run Status: running
      |
      v
Execute Target
      |
      v
Case Results
      |
      +----------------+
      |                |
      v                v
 Completed           Failed
      |
      v
Metric Plugins
      |
      v
Metric Scores
      |
      v
Weighted Overall Score
      |
      v
Quality + Operational Gates
      |
      v
Regression Check
      |
      v
Run Report + History + JSON
```

---

# 🏗️ Architecture

OpenEval follows **Clean Architecture**, keeping evaluation rules independent
from provider infrastructure.

```text
                 Interface
          CLI • Reports • CI
                    |
                    v
                Application
                 Use Cases
                    |
                    v
                  Domain
             Evaluation Rules
                    |
                    v
              Infrastructure
        Providers • Metrics • Storage
```

Dependencies point inward.

Provider execution is interchangeable:

```text
                 TargetExecutor
                      |
          +-----------+-----------+
          |           |           |
          v           v           v
        Mock        Ollama      OpenAI
```

Metric evaluation follows the same plugin-oriented approach:

```text
                  MetricPlugin
                      |
          +-----------+-----------+
          |           |           |
          v           v           v
       accuracy    contains    llm_judge
```

This separation allows execution providers, metrics, reporting, and interfaces
to evolve independently.

---

# 📂 Project Structure

```text
OpenEval/
|
+-- .github/
|   +-- actions/
|   +-- workflows/
|
+-- docs/
+-- examples/
|   +-- basic/
|   +-- llm-judge/
|   +-- weighted-metrics/
|   +-- operational-gates/
|
+-- tests/
|
+-- openeval/
|   +-- application/
|   +-- domain/
|   +-- infrastructure/
|   +-- interface/
|
+-- pyproject.toml
+-- README.md
+-- CONTRIBUTING.md
+-- CODE_OF_CONDUCT.md
+-- ROADMAP.md
```

---

# 🧪 Engineering Quality

Every OpenEval change is validated through:

```bash
black --check .
ruff check .
mypy openeval
pytest
```

The project uses:

- **Ruff** — linting
- **Black** — formatting
- **MyPy** — strict static type checking
- **Pytest** — automated testing
- **GitHub Actions** — continuous integration
- **OpenEval itself** — AI quality validation

The v1.0 release is backed by a growing automated test suite covering scoring,
configuration, operational gates, failure resilience, run lifecycle, pricing,
JSON serialization, provider routing, and quality-gate behavior.

---

# 🖥️ CLI Reference

Check the installed version:

```bash
openeval --version
```

Validate configuration:

```bash
openeval validate evaluation.yaml
```

Run an evaluation:

```bash
openeval run evaluation.yaml
```

Emit JSON:

```bash
openeval run evaluation.yaml --json
```

Write JSON:

```bash
openeval run evaluation.yaml --output results.json
```

Compare providers:

```bash
openeval compare evaluation.yaml \
  --left-provider ollama \
  --right-provider mock
```

View history:

```bash
openeval history
```

Full command help:

```bash
openeval --help
```

---

# 🛣️ Roadmap

## ✅ OpenEval v1.0

- YAML evaluation configuration
- CSV dataset ingestion
- configuration validation
- automatic case generation
- Mock execution
- Ollama execution
- OpenAI execution
- provider routing architecture
- plugin-based metrics
- exact-match accuracy
- short-answer containment scoring
- Ollama LLM-as-a-Judge
- multi-metric evaluation
- weighted metric scoring
- overall quality gates
- per-metric quality gates
- latency gates
- token-budget gates
- API-cost gates
- token usage tracking
- estimated API-cost tracking
- case-level failure resilience
- run lifecycle tracking
- explicit baselines
- historical baselines
- regression detection
- provider/model comparison
- persistent run history
- comparison history
- machine-readable JSON output
- rich HTML run reports
- HTML comparison reports
- CI-compatible exit codes
- GitHub Actions CI
- reusable OpenEval GitHub Action

## 🔮 Beyond v1.0

Potential future directions include:

- additional LLM judge providers
- Anthropic integration
- Gemini integration
- additional dataset formats
- richer judge reasoning and verdict metadata
- benchmark suites
- experiment dashboards
- extended metric plugin ecosystem
- remote evaluation history/storage
- richer model-comparison analytics

The v1.0 scope intentionally focuses on a reliable evaluation engine and
developer workflow rather than a hosted dashboard or web application.

---

# 🎯 Vision

OpenEval aims to make AI quality engineering feel like software quality
engineering.

> ### **GitHub Actions for AI Quality.**

The goal is to make AI quality:

**measurable • reproducible • comparable • versioned • enforceable**

throughout the software development lifecycle.

```text
Developer changes model / prompt / application
                    |
                    v
                 Git Push
                    |
                    v
                  OpenEval
                    |
          +---------+---------+
          |         |         |
          v         v         v
       Dataset    Target    Metrics
          +---------+---------+
                    |
                    v
                Evaluation
                    |
                    v
          Weighted Metric Score
                    |
                    v
        Quality + Operational Gates
                    |
                    v
             Regression Check
                /       \
              PASS      FAIL
               |          |
               v          v
             Merge       Block
```

AI quality should eventually feel as natural to enforce as unit tests.

---

# 🤝 Contributing

Contributions are welcome.

OpenEval may be interesting if you work on:

- AI Evaluation
- AI Reliability
- Trustworthy AI
- AI Infrastructure
- LLM Engineering
- Developer Tooling
- Backend Engineering

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidance.

---

# 📜 License

OpenEval is licensed under the **Apache License 2.0**.

---

<div align="center">

### ⭐ If OpenEval looks useful, consider starring the repository.

**Building reliable AI systems starts with measurable quality.**

</div>