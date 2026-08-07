<div align="center">

# 🚀 OpenEval

### Open-Source AI Evaluation Platform for LLM Applications

**Run evaluations • Compare models • Enforce AI Quality**

<p>

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

[![CI](https://img.shields.io/github/actions/workflow/status/Harshrudrawar/OpenEval/ci.yml?branch=main&style=for-the-badge&label=CI)](https://github.com/Harshrudrawar/OpenEval/actions/workflows/ci.yml)

[![License](https://img.shields.io/badge/License-Apache%202.0-green?style=for-the-badge)](LICENSE)

[![Status](https://img.shields.io/badge/Status-Active%20Development-orange?style=for-the-badge)]()

</p>

*Building reproducible, versioned, and continuously evaluated AI systems.*

</div>

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

Instead of manually checking prompts or comparing responses, OpenEval provides a structured evaluation pipeline that can evolve into your AI quality gate.

---

# ✨ Current Capabilities

OpenEval currently supports:

- YAML-driven evaluations
- CSV dataset loading
- Automatic case generation
- Evaluation and run management
- Mock execution
- Ollama execution
- OpenAI provider architecture
- Plugin-based metrics
- Accuracy metric
- Clean Architecture
- GitHub Actions CI

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

Run

```bash
python -m openeval.interface.cli run examples/basic/evaluation.yaml
```

Example output

```text
✔ Evaluation created successfully

Loaded 3 cases

Created 3 case results

Accuracy: 1.00

Run created successfully
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
 Run Metrics
        │
        ▼
 Display Results
```

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
  - accuracy
```

Supported providers

| Provider | Status |
|----------|:------:|
| Mock | ✅ |
| Ollama | ✅ |
| OpenAI | 🚧 |
| Anthropic | 📋 Planned |
| Gemini | 📋 Planned |

---

# 🏗 Architecture

OpenEval follows **Clean Architecture**.

```text
               Interface
         (CLI • REST • GitHub)

                 │
                 ▼

            Application
             (Use Cases)

                 │
                 ▼

               Domain
        (Business Rules)

                 │
                 ▼

          Infrastructure
 (Providers • Plugins • Storage)
```

Dependencies always point inward.

---

# 📂 Project Structure

```text
OpenEval/

├── docs/
├── examples/
├── tests/

├── openeval/
│   ├── application/
│   ├── domain/
│   ├── infrastructure/
│   └── interface/

├── pyproject.toml
└── README.md
```

---

# 🛣 Roadmap

## ✅ Completed

- YAML configuration
- Dataset loading
- Case generation
- Evaluation pipeline
- Run management
- Mock provider
- Ollama provider
- Accuracy metric
- Plugin architecture
- GitHub Actions

---

## 🚧 In Progress

- OpenAI execution
- Model comparison
- Rich evaluation summaries

---

## 🔮 Planned

- HTML reports
- Cost tracking
- Latency tracking
- Quality Gates
- GitHub Action
- Experiment history
- Benchmarking
- LLM-as-a-Judge
- Anthropic support
- Gemini support

---

# 🎯 Vision

OpenEval aims to become

> **GitHub Actions for AI Quality.**

The long-term goal is to make AI quality measurable, reproducible, versioned, and enforceable throughout the software development lifecycle.

---

# 🤝 Contributing

Contributions are welcome.

Whether you're interested in:

- AI Infrastructure
- AI Evaluation
- Developer Tooling
- Backend Engineering
- Clean Architecture

feel free to open an issue or submit a pull request.

---

# 📜 License

Apache License 2.0

---

<div align="center">

### ⭐ Star the repository if you find OpenEval useful.

**Building reliable AI systems starts with measurable quality.**

</div>