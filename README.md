<div align="center">

# 🚀 OpenEval

### Open-Source AI Evaluation & Quality Platform for LLM Applications

**Evaluate models • Compare providers • Judge responses • Detect regressions • Enforce AI quality**

<br>

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![CI](https://img.shields.io/github/actions/workflow/status/Harshrudrawar/OpenEval/ci.yml?branch=main&style=for-the-badge&label=CI)](https://github.com/Harshrudrawar/OpenEval/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-Apache%202.0-green?style=for-the-badge)](LICENSE)
![Status](https://img.shields.io/badge/Status-Active%20Development-orange?style=for-the-badge)

<br>

**Building reproducible, comparable, and continuously evaluated AI systems.**

</div>

---

## 💡 Why OpenEval?

Traditional software engineering has:

**Unit Tests → Integration Tests → CI/CD → Quality Gates**

AI applications need the same engineering discipline.

LLM systems are probabilistic. Prompt changes, model upgrades, provider changes, and application updates can improve one behavior while silently degrading another.

OpenEval provides a structured evaluation workflow for LLM applications so developers can:

- run reproducible evaluations
- score outputs with multiple metrics
- use LLMs as evaluation judges
- compare providers and models
- enforce minimum quality thresholds
- detect regressions against previous runs
- generate evaluation reports
- integrate AI quality checks directly into CI

Instead of asking:

> **"Does this model seem better?"**

OpenEval moves toward answering:

> **"Did AI quality improve, regress, or fail our required threshold?"**

---

## ✨ What OpenEval Can Do Today

| Capability | Status |
| --- | :---: |
| YAML-driven evaluations | ✅ |
| CSV dataset loading | ✅ |
| Automatic case generation | ✅ |
| Mock execution | ✅ |
| Local Ollama execution | ✅ |
| Provider-based execution architecture | ✅ |
| Exact-match accuracy | ✅ |
| Short-answer containment scoring | ✅ |
| **Multi-metric evaluation** | ✅ |
| **LLM-as-a-Judge with Ollama** | ✅ |
| **Overall multi-metric scoring** | ✅ |
| Provider/model comparison | ✅ |
| Latency tracking | ✅ |
| Quality gates | ✅ |
| **Historical baselines** | ✅ |
| **Regression detection** | ✅ |
| **Run & comparison history** | ✅ |
| CI-compatible exit codes | ✅ |
| Rich HTML run reports | ✅ |
| HTML comparison reports | ✅ |
| GitHub Actions CI | ✅ |
| **Reusable OpenEval GitHub Action** | ✅ |
| Pull-request quality checks | ✅ |

---

# ⚡ Quick Start

### 1. Clone OpenEval

```bash
git clone https://github.com/Harshrudrawar/OpenEval.git
cd OpenEval
```

### 2. Install

```bash
pip install -e .
```

### 3. Run an evaluation

```bash
python -m openeval.interface.cli run examples/basic/evaluation.yaml
```

Example output:

```text
✔ Evaluation created successfully

ID: <evaluation-id>
Name: Demo Evaluation
Dataset Version: dataset-v1
Prompt Version: prompt-v1
Metrics: 1

Loaded 3 cases
Created 3 case results
Overall Score: 1.00

Metric Scores:
  contains: 1.00

Latency: 3 ms
Quality Gate: PASSED (threshold: 0.80)

Run created successfully
Run ID: <run-id>
Run Status: created

Report written to: reports/<run-id>.html
History written to: reports/run-history.jsonl
```

Every run can produce a standalone HTML evaluation report and a persistent history record.

---

# ⚙️ Evaluation Configuration

OpenEval evaluations are defined using YAML.

```yaml
name: Demo Evaluation

dataset:
  version: dataset-v1
  path: examples/basic/dataset.csv

prompt:
  version: prompt-v1

target:
  provider: mock

metrics:
  - contains

gate:
  accuracy: 0.80
```

The configuration defines the evaluation contract:

```text
Dataset
   +
Prompt Version
   +
Target Provider
   +
Evaluation Metrics
   +
Quality Gate
```

This makes evaluations reproducible and version-aware instead of relying on ad-hoc manual testing.

---

# 🧠 Multi-Metric Evaluation

Real AI quality rarely fits into a single metric.

OpenEval can evaluate the same model output using multiple scoring strategies:

```yaml
metrics:
  - contains
  - llm_judge

judge:
  provider: ollama
  model: llama3
```

The target is executed once.

The resulting outputs are then evaluated independently by every configured metric:

```text
                     Target
                       │
                       ▼
                 Execute Cases
                       │
                       ▼
                  Case Results
                       │
             ┌─────────┴─────────┐
             │                   │
             ▼                   ▼
          contains           llm_judge
             │                   │
             ▼                   ▼
            1.00                0.92
             │                   │
             └─────────┬─────────┘
                       │
                       ▼
                  Overall Score
                       │
                       ▼
                  Quality Gate
```

For the current multi-metric implementation:

```text
Overall Score = average of configured metric scores
```

Example:

```text
Metric Scores:
  contains: 1.00
  llm_judge: 0.92

Overall Score: 0.96
```

This allows deterministic and semantic evaluation strategies to work together.

---

# 🧠 LLM-as-a-Judge

Exact matching is useful, but many valid LLM answers are semantically correct without matching the expected text exactly.

OpenEval supports an **LLM-as-a-Judge** metric using a local Ollama model.

Example:

```text
Expected:
Paris is the capital of France.

Actual:
France's capital city is Paris.
```

An exact-match metric may reject the answer.

An LLM judge can evaluate whether the response is semantically correct.

Configure it with:

```yaml
metrics:
  - llm_judge

judge:
  provider: ollama
  model: llama3
```

The evaluation flow becomes:

```text
Expected Output
      +
Actual Output
      │
      ▼
LLM Judge Metric
      │
      ▼
Ollama / llama3
      │
      ▼
Structured Verdict
      │
      ▼
0.0 / 1.0 Score
```

The judge is intentionally separate from the target being evaluated.

For example:

```yaml
target:
  provider: mock

metrics:
  - llm_judge

judge:
  provider: ollama
  model: llama3
```

Here the **mock target** generates the result while **Ollama acts as the evaluator**.

This separation makes it possible to evaluate one model using another model as the judge.

---

# 📏 Evaluation Metrics

OpenEval currently provides three metric strategies.

### Exact-Match Accuracy

Useful when expected and generated values should match exactly.

```text
Expected: Paris
Actual:   Paris

Score: 1.0
```

Matching is normalized for casing and surrounding whitespace.

Configure with:

```yaml
metrics:
  - accuracy
```

### Short-Answer Containment

Useful when an LLM produces additional natural language around a correct short answer.

```text
Expected:
Paris

Actual:
"The capital of France is Paris."

Score: 1.0
```

Configure with:

```yaml
metrics:
  - contains
```

### LLM Judge

Useful when semantic correctness matters more than exact wording.

```yaml
metrics:
  - llm_judge

judge:
  provider: ollama
  model: llama3
```

The metric layer is plugin-based, allowing new evaluation strategies to be introduced without rewriting the execution pipeline.

---

# 🔌 Execution Providers

OpenEval separates model execution from evaluation logic.

| Provider | Status | Use Case |
| --- | :---: | --- |
| **Mock** | ✅ | Deterministic tests and CI |
| **Ollama** | ✅ | Local LLM execution |
| **OpenAI** | 🟡 | Provider architecture / cloud execution |
| **Anthropic** | 🔜 | Planned |
| **Gemini** | 🔜 | Planned |

### Local Ollama

```yaml
target:
  provider: ollama
  model: llama3
```

Ollama is especially useful for local experimentation without requiring cloud API usage.

### OpenAI

The provider architecture is designed to support cloud model execution through provider-specific executors.

Secrets should be supplied through environment variables rather than stored inside evaluation YAML.

---

# 🔀 Compare Models & Providers

Run the **same dataset, prompt version, and metric configuration** against two providers:

```bash
python -m openeval.interface.cli compare examples/basic/evaluation.yaml \
  --left-provider ollama \
  --right-provider mock
```

Example:

```text
✔ Comparison completed successfully

Dataset Version: dataset-v1
Prompt Version: prompt-v1

Left  (ollama:llama3): 0.67
Right (mock:unknown): 1.00

Winner: mock:unknown
Margin: 0.33

Report written to:
reports/comparison-<evaluation-id>.html
```

This makes model and provider decisions measurable rather than subjective.

---

# 🛡️ AI Quality Gates

Evaluation should do more than produce a score.

OpenEval can enforce minimum quality requirements:

```yaml
gate:
  accuracy: 0.80
```

With multi-metric evaluation, the gate currently applies to the overall evaluation score.

### Passing evaluation

```text
Overall Score: 0.93
Quality Gate: PASSED
```

Process result:

```text
exit code 0
```

### Failing evaluation

```text
Overall Score: 0.72
Quality Gate: FAILED
```

Process result:

```text
exit code 1
```

That means OpenEval can participate directly in CI/CD:

```text
                 AI Application Change
                          │
                          ▼
                       OpenEval
                          │
                          ▼
                    Run Evaluation
                          │
                          ▼
                     Quality Gate
                      /         \
                     /           \
                  PASS           FAIL
                   │               │
                   ▼               ▼
              Continue CI       Exit 1
                                   │
                                   ▼
                            Block Pipeline
```

---

# 📉 Regression Detection

A model can still pass a minimum quality threshold while performing worse than a previous version.

OpenEval supports regression checks to detect that situation.

Example:

```yaml
regression:
  max_drop: 0.05
```

An explicit baseline can be configured:

```yaml
baseline:
  provider: mock
  model: baseline
```

Example output:

```text
Baseline Regression Check

Baseline (mock:baseline): 1.00
Current  (ollama:llama3): 0.67
Delta: -0.33
Result: REGRESSED
Allowed Drop: 0.05
Regression Gate: FAILED
```

This provides a second layer of protection:

```text
Current Evaluation
        │
        ├──────────────► Quality Threshold
        │
        ▼
Historical / Explicit Baseline
        │
        ▼
Regression Delta
        │
        ▼
Regression Gate
```

---

# 🕘 Historical Baselines

OpenEval can also use previous successful runs as baselines.

```yaml
baseline:
  source: history

regression:
  max_drop: 0.05
```

OpenEval searches compatible historical runs using evaluation context such as:

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

This allows regression detection to evolve with the evaluation history rather than requiring a hard-coded baseline forever.

---

# 🗂️ Evaluation History

OpenEval stores run and comparison history in:

```text
reports/run-history.jsonl
```

View history with:

```bash
python -m openeval.interface.cli history
```

Filter to runs:

```bash
python -m openeval.interface.cli history --kind run
```

Filter to comparisons:

```bash
python -m openeval.interface.cli history --kind comparison
```

Example:

```text
OpenEval History

RUN
Evaluation: Demo Evaluation
Provider: mock
Model: unknown
Metrics: contains
Accuracy: 1.00
Gate: PASSED
Regression: PASSED
```

History records preserve evaluation context so previous runs can be inspected and reused for regression analysis.

---

# 📊 Rich HTML Reports

OpenEval generates standalone HTML reports for evaluation runs.

Run reports include:

- overall score
- individual metric scores
- target provider and model
- judge provider and model when applicable
- dataset version
- prompt version
- case count
- latency
- quality gate status
- evaluation/run identifiers

For multi-metric evaluations, the report shows each metric independently:

```text
Metric Scores

contains       1.00
llm_judge      0.92

Overall        0.96
```

Comparison runs generate dedicated reports containing:

- both providers/models
- individual overall scores
- winning configuration
- score margin
- dataset version
- prompt version

Reports are generated under:

```text
reports/
```

and are intentionally excluded from Git tracking.

---

# ⚙️ GitHub Actions

OpenEval can run directly inside CI.

The repository itself runs:

```text
Ruff
  │
  ▼
Black
  │
  ▼
MyPy
  │
  ▼
Pytest
  │
  ▼
OpenEval Quality Check
  │
  ▼
Upload Evaluation Reports
```

This means OpenEval **dogfoods its own evaluation system** as part of repository CI.

---

# 🧩 Reusable OpenEval GitHub Action

OpenEval can also be consumed from another GitHub repository.

Example:

```yaml
- uses: Harshrudrawar/OpenEval/.github/actions/openeval@v1
  with:
    config: examples/basic/evaluation.yaml
```

A consuming repository can therefore make AI evaluation part of its normal software delivery workflow.

Conceptually:

```text
Pull Request
     │
     ▼
GitHub Actions
     │
     ▼
OpenEval
     │
     ▼
Evaluation
     │
     ▼
Quality Gate
   /       \
 PASS      FAIL
  │          │
  ▼          ▼
Merge      Block
```

This is a core part of OpenEval's long-term direction:

> **Treat AI quality checks like software quality checks.**

---

# 🔄 Evaluation Pipeline

```text
                    evaluation.yaml
                          │
                          ▼
                  Load Configuration
                          │
                          ▼
                     Load Dataset
                          │
                          ▼
                    Generate Cases
                          │
                          ▼
                  Create Evaluation
                          │
                          ▼
                      Create Run
                          │
                          ▼
                   Execute Provider
                          │
                          ▼
                 Generate Case Results
                          │
                          ▼
                ┌─────────┴─────────┐
                │                   │
                ▼                   ▼
          Metric Plugin        Metric Plugin
                │                   │
                └─────────┬─────────┘
                          │
                          ▼
                    Metric Scores
                          │
                          ▼
                    Overall Score
                          │
                          ▼
                     Quality Gate
                          │
                          ▼
                  Regression Check
                          │
                          ▼
                Report + Run History
```

The target executes once and the resulting case outputs can be evaluated by multiple metric plugins.

---

# 🏗️ Architecture

OpenEval follows **Clean Architecture**, keeping evaluation rules independent from provider infrastructure.

```text
                     Interface
              CLI • Reports • CI
                         │
                         ▼
                    Application
                     Use Cases
                         │
                         ▼
                       Domain
                 Evaluation Rules
                         │
                         ▼
                  Infrastructure
            Providers • Metrics • Storage
```

Dependencies point inward.

Provider execution is interchangeable:

```text
                    TargetExecutor
                         │
             ┌───────────┼───────────┐
             ▼           ▼           ▼
           Mock        Ollama      OpenAI
```

Metric evaluation follows the same plugin-oriented approach:

```text
                     MetricPlugin
                         │
             ┌───────────┼──────────────┐
             ▼           ▼              ▼
         accuracy     contains       llm_judge
```

This allows providers and evaluation strategies to evolve independently.

---

# 📂 Project Structure

```text
OpenEval/
│
├── .github/
│   ├── actions/
│   │   └── openeval/
│   └── workflows/
│
├── docs/
├── examples/
│   ├── basic/
│   └── llm-judge/
│
├── tests/
│
├── openeval/
│   ├── application/
│   ├── domain/
│   ├── infrastructure/
│   └── interface/
│
├── pyproject.toml
└── README.md
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
- **MyPy** — static type checking
- **Pytest** — automated testing
- **GitHub Actions** — continuous integration
- **OpenEval itself** — AI quality validation

The repository's own CI executes an OpenEval evaluation and uploads generated reports as workflow artifacts.

---

# 🛣️ Roadmap

## ✅ Built

- YAML evaluation configuration
- CSV dataset ingestion
- Automatic case generation
- Evaluation and run management
- Mock execution
- Ollama execution
- Provider routing architecture
- Plugin-based metrics
- Exact-match accuracy
- Short-answer containment scoring
- **Multi-metric evaluation**
- **Overall metric aggregation**
- **Ollama LLM-as-a-Judge**
- Provider/model comparison
- Latency measurement
- Quality gates
- CI-compatible exit codes
- **Explicit baselines**
- **Historical baselines**
- **Regression detection**
- **Persistent run history**
- **Comparison history**
- Rich HTML run reports
- HTML comparison reports
- GitHub Actions CI
- **Reusable OpenEval GitHub Action**
- **Pull-request quality checks**
- Automated quality-gate testing

## 🚧 Next

- Per-metric quality gates
- Weighted metric scoring
- Richer LLM judge verdicts and reasoning
- Better provider failure handling
- Cost and token tracking
- Improved comparison reports

## 🔮 Future

- Additional LLM judge providers
- Anthropic integration
- Gemini integration
- Additional dataset formats
- Benchmark suites
- Experiment dashboards
- Extended metric plugin ecosystem
- Remote evaluation history/storage

---

# 🎯 Vision

OpenEval aims to become:

> ### **GitHub Actions for AI Quality.**

The goal is to make AI quality:

**measurable • reproducible • comparable • versioned • enforceable**

throughout the software development lifecycle.

```text
Developer changes model / prompt / application
                    │
                    ▼
                 Git Push
                    │
                    ▼
                 OpenEval
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
       Dataset    Target    Metrics
          └─────────┼─────────┘
                    ▼
                Evaluation
                    │
                    ▼
             Multi-Metric Score
                    │
                    ▼
              Quality Gate
                    │
                    ▼
            Regression Check
                /       \
             PASS       FAIL
               │          │
               ▼          ▼
             Merge      Block
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

Feel free to open an issue, propose a metric, add a provider, improve evaluation infrastructure, or submit a pull request.

---

# 📜 License

OpenEval is licensed under the **Apache License 2.0**.

---

<div align="center">

### ⭐ If OpenEval looks useful, consider starring the repository.

**Building reliable AI systems starts with measurable quality.**

</div>