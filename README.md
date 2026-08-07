<div align="center">

# 🚀 OpenEval

### Open-Source AI Evaluation & Quality Platform for LLM Applications

**Evaluate models • Compare providers • Generate reports • Enforce quality gates**

<br>

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![CI](https://img.shields.io/github/actions/workflow/status/Harshrudrawar/OpenEval/ci.yml?branch=main&style=for-the-badge&label=CI)](https://github.com/Harshrudrawar/OpenEval/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-Apache%202.0-green?style=for-the-badge)](LICENSE)
![Status](https://img.shields.io/badge/Status-Active%20Development-orange?style=for-the-badge)

<br>

*Building reproducible, comparable, and continuously evaluated AI systems.*

</div>

---

## 💡 Why OpenEval?

Traditional software engineering has:

**Unit Tests → Integration Tests → CI/CD → Quality Gates**

AI applications need the same discipline.

OpenEval provides a structured evaluation workflow for LLM applications so developers can measure model quality, compare providers, generate evaluation reports, and enforce minimum quality requirements before changes move forward.

Instead of asking:

> *"Does this model seem better?"*

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
| OpenAI provider integration | ✅ |
| Configurable evaluation metrics | ✅ |
| Exact-match accuracy | ✅ |
| Short-answer containment scoring | ✅ |
| Provider/model comparison | ✅ |
| Latency tracking | ✅ |
| Quality gates | ✅ |
| CI-compatible exit codes | ✅ |
| HTML run reports | ✅ |
| HTML comparison reports | ✅ |
| GitHub Actions CI | ✅ |

---

## ⚡ Quick Start

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

Example:

```text
✔ Evaluation created successfully

Loaded 3 cases
Created 3 case results

Accuracy: 1.00
Latency: 3 ms
Quality Gate: PASSED (threshold: 0.80)

Run created successfully

Run ID: <generated-run-id>
Run Status: created

Report written to: reports/<run-id>.html
```

OpenEval also generates an HTML report for the run.

---

## ⚙️ Evaluation Configuration

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

The configuration describes:

```text
Dataset
   +
Prompt Version
   +
Target Provider
   +
Evaluation Metric
   +
Quality Gate
```

---

## 🔌 Execution Providers

OpenEval separates evaluation logic from model execution.

| Provider | Status | Use Case |
| --- | :---: | --- |
| **Mock** | ✅ | Deterministic tests and CI |
| **Ollama** | ✅ | Free local LLM evaluation |
| **OpenAI** | 🟡 | Cloud model evaluation |
| **Anthropic** | 🔜 | Planned |
| **Gemini** | 🔜 | Planned |

### Local Ollama

```yaml
target:
  provider: ollama
  model: llama3
```

### OpenAI

```yaml
target:
  provider: openai
  model: gpt-4o
```

OpenAI execution requires API access through the `OPENAI_API_KEY` environment variable.

Secrets are never stored inside the evaluation YAML.

---

## 🧠 Evaluation Metrics

OpenEval currently supports deterministic metrics designed for different evaluation scenarios.

### Exact-Match Accuracy

Useful when the expected and generated values should match exactly.

```text
Expected: Paris
Actual:   Paris

Score: 1.0
```

Matching is normalized for casing and surrounding whitespace.

### Short-Answer Containment

Useful when an LLM produces additional natural language around a correct answer.

```text
Expected: Paris

Actual:
"The capital of France is Paris."

Score: 1.0
```

Configure it with:

```yaml
metrics:
  - contains
```

The metric layer is plugin-based so additional evaluation strategies can be introduced without changing the execution pipeline.

---

## 🔀 Compare Models & Providers

Run the **same dataset and evaluation configuration** against two providers:

```bash
python -m openeval.interface.cli compare examples/basic/evaluation.yaml \
  --left-provider ollama \
  --right-provider mock
```

Example output:

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

This allows different providers or models to be evaluated under the **same dataset and metric conditions**.

---

## 🛡️ AI Quality Gates

Evaluation should do more than produce a number.

OpenEval can enforce minimum quality requirements:

```yaml
gate:
  accuracy: 0.80
```

### Passing evaluation

```text
Accuracy: 0.93

Quality Gate: PASSED
```

Process result:

```text
exit code 0
```

### Failing evaluation

```text
Accuracy: 0.72

Quality Gate: FAILED
```

Process result:

```text
exit code 1
```

That enables OpenEval to participate directly in CI/CD:

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
                    /       \
                   /         \
                PASS         FAIL
                 │             │
                 ▼             ▼
            Continue CI    Exit Code 1
                               │
                               ▼
                          Block Pipeline
```

---

## 📊 HTML Reports

Every evaluation can generate a standalone HTML report containing:

- Evaluation metadata
- Provider and model
- Dataset version
- Prompt version
- Number of evaluation cases
- Metric score
- Latency
- Quality gate status
- Run information

Comparison runs generate dedicated reports containing:

- Both providers/models
- Individual scores
- Winning configuration
- Score margin
- Dataset version
- Prompt version

Reports are generated locally under:

```text
reports/
```

and are intentionally excluded from Git tracking.

---

## 🔄 Evaluation Pipeline

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
                    Evaluate Metric
                           │
                           ▼
                     Quality Gate
                       /       \
                      /         \
                   PASS         FAIL
                     │            │
                     ▼            ▼
              Generate Report   Exit 1
```

---

## 🏗️ Architecture

OpenEval follows **Clean Architecture**, keeping evaluation rules independent from providers and infrastructure.

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

Provider execution is interchangeable:

```text
                   TargetExecutor
                         │
             ┌───────────┼───────────┐
             ▼           ▼           ▼
           Mock        Ollama      OpenAI
```

This allows new providers to be added without rewriting the evaluation pipeline.

---

## 📂 Project Structure

```text
OpenEval/
│
├── .github/
│   └── workflows/
│
├── docs/
├── examples/
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

## 🧪 Engineering Quality

OpenEval validates every change through:

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
OpenEval Evaluation
```

The repository uses:

- **Ruff** — linting
- **Black** — formatting
- **MyPy** — strict static type checking
- **Pytest** — automated testing
- **GitHub Actions** — continuous integration

OpenEval also executes its own example evaluation inside CI.

---

## 🛣️ Roadmap

### ✅ Built

- YAML evaluation configuration
- CSV dataset ingestion
- Case generation
- Evaluation execution pipeline
- Run management
- Mock execution
- Ollama integration
- OpenAI provider integration
- Provider routing
- Configurable metrics
- Accuracy scoring
- Short-answer containment scoring
- Latency measurement
- Quality gates
- CI-compatible exit codes
- HTML run reports
- Provider/model comparison
- HTML comparison reports
- GitHub Actions integration
- Automated quality-gate testing

### 🚧 Next

- More robust LLM evaluation metrics
- Better provider failure handling
- Baseline comparison
- Regression detection
- Improved evaluation reports

### 🔮 Future

- LLM-as-a-Judge
- Cost tracking
- Experiment history
- Anthropic integration
- Gemini integration
- Dedicated OpenEval GitHub Action
- Pull-request quality checks
- Additional dataset formats
- Extended metric plugin ecosystem

---

## 🎯 Vision

OpenEval aims to become:

> ### **GitHub Actions for AI Quality.**

The goal is to make AI quality **measurable, reproducible, comparable, versioned, and enforceable** throughout the software development lifecycle.

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
       Dataset    Model     Metrics
          └─────────┼─────────┘
                    ▼
              Evaluation
                    │
                    ▼
               Comparison
                    │
                    ▼
              Quality Gate
                /       \
             PASS       FAIL
               │          │
               ▼          ▼
             Merge      Block
```

AI quality should eventually feel as natural to enforce as unit tests.

---

## 🤝 Contributing

Contributions are welcome.

OpenEval may be interesting if you work on:

- AI Evaluation
- AI Reliability
- AI Infrastructure
- LLM Engineering
- Developer Tooling
- Backend Engineering

Feel free to open an issue or submit a pull request.

---

## 📜 License

OpenEval is licensed under the **Apache License 2.0**.

---

<div align="center">

### ⭐ If OpenEval looks useful, consider starring the repository.

**Building reliable AI systems starts with measurable quality.**

</div>