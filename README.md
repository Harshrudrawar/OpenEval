# 🚀 OpenEval

### Open-Source AI Evaluation Platform for LLM Applications

**Run evaluations • Compare models • Enforce AI Quality**

*Building reproducible, versioned, and continuously evaluated AI systems.*

---

# Why OpenEval?

Modern software has:

- Unit Tests
- Integration Tests
- CI/CD Pipelines

Modern AI systems deserve the same engineering discipline.

OpenEval brings automated evaluation to Large Language Model applications by making AI quality:

- **Reproducible**
- **Versioned**
- **Comparable**
- **Continuously Evaluated**
- **Enforceable**

Instead of manually checking prompts, comparing model responses, or relying on one-off evaluation scripts, OpenEval provides a structured evaluation pipeline designed to integrate AI quality into the software development lifecycle.

---

# ✨ Current Capabilities

OpenEval currently supports:

- YAML-driven evaluations
- CSV dataset loading
- Automatic case generation
- Evaluation and run management
- Multiple execution providers
- Mock execution for deterministic testing and CI
- Local LLM execution with Ollama
- OpenAI provider integration
- Configurable metric selection
- Normalized exact-match accuracy
- Short-answer containment scoring
- Quality gates with CI-compatible exit codes
- Latency tracking
- HTML evaluation reports
- Side-by-side provider and model comparison
- HTML comparison reports
- Plugin-based metrics
- Clean Architecture
- GitHub Actions CI
- Ruff, Black, MyPy, and Pytest validation

---

# ⚡ Quick Start

Clone

```bash
git clone https://github.com/Harshrudrawar/OpenEval.git
cd OpenEval
```

Install

```bash
pip install -e .
```

Run an evaluation

```bash
python -m openeval.interface.cli run examples/basic/evaluation.yaml
```

Example output

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

---

# ⚙️ Evaluation Pipeline

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
 Evaluate Metrics
        │
        ▼
 Check Quality Gate
        │
        ▼
 Generate HTML Report
        │
        ▼
 Pass / Fail
```

A failed quality gate returns a non-zero process exit code, allowing OpenEval evaluations to participate directly in CI pipelines.

---

# 📄 Example Configuration

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

The same evaluation configuration can be used with different execution providers.

For local Ollama execution:

```yaml
target:
  provider: ollama
  model: llama3
```

For OpenAI execution:

```yaml
target:
  provider: openai
  model: gpt-4o
```

OpenAI execution requires a valid `OPENAI_API_KEY` with API access.

---

# 🧠 Metrics

OpenEval currently provides two deterministic scoring modes.

### Accuracy

Normalized exact-match evaluation.

```text
Expected: "Paris"
Actual:   "Paris"

Score: 1.0
```

Case and surrounding whitespace are normalized before comparison.

### Contains

Designed for short-answer evaluation where LLMs may return additional natural language.

```text
Expected: "Paris"
Actual:   "The capital of France is Paris."

Score: 1.0
```

Select the metric directly from `evaluation.yaml`:

```yaml
metrics:
  - contains
```

The metric system is plugin-based so additional evaluation strategies can be introduced without changing the execution pipeline.

---

# 🔀 Model Comparison

OpenEval can execute the same evaluation against two providers and compare their results.

Example:

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

Report written to: reports/comparison-<evaluation-id>.html
```

Both providers run against the same dataset and metric configuration, allowing side-by-side evaluation under consistent conditions.

---

# 🛡️ Quality Gates

OpenEval can enforce minimum quality requirements directly from the evaluation configuration.

```yaml
gate:
  accuracy: 0.80
```

If the evaluation meets the threshold:

```text
Quality Gate: PASSED (threshold: 0.80)
```

OpenEval exits successfully.

If quality drops below the threshold:

```text
Quality Gate: FAILED (threshold: 0.80)
```

OpenEval returns a non-zero exit code.

This makes evaluation results usable as CI/CD quality checks rather than passive metrics.

```text
Model / Application Change
          │
          ▼
      OpenEval Run
          │
          ▼
     Evaluate Quality
          │
          ▼
      Quality Gate
       /        \
    PASS        FAIL
     │            │
     ▼            ▼
Continue      Exit Code 1
```

---

# 📊 Evaluation Reports

Every evaluation can generate an HTML report containing:

- Evaluation metadata
- Provider and model
- Dataset version
- Prompt version
- Number of cases
- Accuracy
- Latency
- Quality gate status
- Run information

Reports are generated under:

```text
reports/
```

Generated reports are runtime artifacts and are excluded from Git tracking.

Model comparisons also generate dedicated HTML comparison reports showing:

- Left provider/model
- Right provider/model
- Individual scores
- Winner
- Score margin
- Dataset version
- Prompt version

---

# 🔌 Providers

| Provider | Status | Intended Use |
| --- | :---: | --- |
| Mock | ✅ | Deterministic tests and CI |
| Ollama | ✅ | Free local LLM evaluation |
| OpenAI | 🟡 | Cloud LLM execution |
| Anthropic | 🔜 | Planned |
| Gemini | 🔜 | Planned |

The provider layer is designed around a common execution interface, allowing evaluation logic to remain independent of the model provider.

---

# 🏗 Architecture

OpenEval follows **Clean Architecture**, keeping evaluation logic independent from infrastructure and model providers.

```text
               Interface
          (CLI • Reports • CI)

                  │
                  ▼

             Application
              (Use Cases)

                  │
                  ▼

                Domain
         (Evaluation Rules)

                  │
                  ▼

           Infrastructure
    (Providers • Metrics • Storage)
```

Provider implementations remain interchangeable behind the same execution contract.

```text
                 TargetExecutor
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
        Mock         Ollama       OpenAI
```

---

# 📂 Project Structure

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

# 🧪 Engineering Quality

OpenEval's CI pipeline validates every change with:

```text
Ruff
  ↓
Black
  ↓
MyPy
  ↓
Pytest
  ↓
OpenEval Evaluation
```

The project currently uses:

- **Ruff** for linting
- **Black** for formatting
- **MyPy** with strict type checking
- **Pytest** for automated testing
- **GitHub Actions** for continuous integration

OpenEval also runs its own example evaluation inside CI, meaning the project uses its evaluation workflow as part of its own validation process.

---

# 🛣 Roadmap

## ✅ Completed

- YAML evaluation configuration
- CSV dataset loading
- Case generation
- Evaluation pipeline
- Run management
- Mock provider
- Ollama provider
- OpenAI provider integration
- Provider routing
- Accuracy metric
- Contains metric
- Configurable metric selection
- Latency tracking
- Quality gates
- CI-compatible failure exit codes
- HTML run reports
- Provider/model comparison
- HTML comparison reports
- Plugin architecture
- GitHub Actions integration
- Automated quality-gate testing

---

## 🚧 In Progress

- More meaningful LLM evaluation metrics
- Improved comparison summaries
- Provider error handling
- Evaluation developer experience

---

## 🔮 Planned

- LLM-as-a-Judge
- Cost tracking
- Baseline comparison
- Experiment history
- Regression detection
- Anthropic support
- Gemini support
- Dedicated GitHub Action
- Pull request quality checks
- Additional dataset formats
- Extended metric plugin ecosystem

---

# 🎯 Vision

OpenEval aims to become:

> **GitHub Actions for AI Quality.**

The long-term goal is to make AI quality measurable, reproducible, comparable, versioned, and enforceable throughout the software development lifecycle.

The intended workflow is simple:

```text
Developer Change
       │
       ▼
    Git Push
       │
       ▼
    OpenEval
       │
       ▼
Dataset + Model + Metrics
       │
       ▼
Evaluation Report
       │
       ▼
Quality Gate
    /      \
 PASS      FAIL
  │          │
  ▼          ▼
Merge      Block
```

AI quality should eventually feel as natural to enforce as unit tests and integration tests.

---

# 🤝 Contributing

Contributions are welcome.

Whether you're interested in:

- AI Infrastructure
- AI Evaluation
- LLM Reliability
- Developer Tooling
- Backend Engineering
- Clean Architecture

feel free to open an issue or submit a pull request.

---

# 📜 License

Apache License 2.0

---

### ⭐ Star the repository if you find OpenEval useful.

**Building reliable AI systems starts with measurable quality.**