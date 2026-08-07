<div align="center">

# 🚀 OpenEval

### Open-Source AI Evaluation Platform for LLM Applications

**Run evaluations • Compare models • Enforce AI Quality**

<p align="center">

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-green?style=for-the-badge)](LICENSE)
[![CI](https://github.com/Harshrudrawar/OpenEval/actions/workflows/ci.yml/badge.svg)](https://github.com/Harshrudrawar/OpenEval/actions/workflows/ci.yml)
[![Status](https://img.shields.io/badge/Status-Active%20Development-orange?style=for-the-badge)]()

</p>

*Building reproducible, versioned, and continuously evaluated AI systems.*

</div>

---

## 📖 Overview

Modern software has automated testing.

Modern AI systems should too.

OpenEval is an open-source platform that helps developers **evaluate, benchmark, and continuously measure the quality of LLM applications**.

Instead of manually comparing prompts or checking model outputs, OpenEval provides a structured evaluation pipeline that can eventually become part of your CI/CD workflow.

---

## ✨ Current Capabilities

OpenEval currently supports:

- YAML-driven evaluation configuration
- CSV dataset loading
- Automatic case generation
- Evaluation and run management
- Multiple execution providers
  - Mock
  - Ollama
  - OpenAI (architecture ready)
- Plugin-based metric system
- Accuracy metric
- Clean Architecture
- GitHub Actions CI
- Ruff + Black + MyPy + Pytest

---

## ⚡ Quick Start

Clone the repository

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

ID: d6bbcd41-9185-48a6-8253-7c275e34cb18

Name: Demo Evaluation

Dataset Version: dataset-v1

Prompt Version: prompt-v1

Metrics: 1

Loaded 3 cases

Created 3 case results

Accuracy: 1.00

Run created successfully

Run ID: dfbe268c-9fa0-4dee-bb0a-55e6a8e98d9b

Run Status: created
```

---

## ⚙️ Evaluation Workflow

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
 Display Results
```

---

## 📄 Example Configuration

```yaml
name: Demo Evaluation

dataset:
  version: dataset-v1
  path: examples/basic/dataset.csv

prompt:
  version: prompt-v1

target:
  provider: mock
  model: llama3

metrics:
  - accuracy
```

Supported providers

| Provider | Status |
|----------|--------|
| Mock | ✅ |
| Ollama | ✅ |
| OpenAI | 🚧 |
| Anthropic | Planned |
| Gemini | Planned |

---

## 🏗 Architecture

OpenEval follows **Clean Architecture**, ensuring that business logic remains independent of infrastructure and frameworks.

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

## 📂 Project Structure

```text
OpenEval/

├── docs/
├── examples/
├── tests/

├── openeval/
│
├── application/
├── domain/
├── infrastructure/
└── interface/

├── pyproject.toml
└── README.md
```

---

## 🎯 Design Principles

OpenEval is built around a few core principles.

- Version everything.
- Evaluate continuously.
- Keep business logic framework-independent.
- Prefer extensible plugin systems.
- Build complete vertical slices.
- Keep the CI pipeline green.
- Optimize for developer experience.

---

## 🛣 Roadmap

### ✅ Foundation

- Clean Architecture
- Domain Model
- YAML configuration
- CLI
- Dataset loading
- Case generation
- Evaluation pipeline
- Run management
- Mock provider
- Ollama provider
- Accuracy metric
- GitHub Actions

---

### 🚧 In Progress

- OpenAI execution
- Model comparison
- Rich evaluation summaries

---

### 🔜 Planned

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

## 🌟 Long-Term Vision

OpenEval aims to become:

> **GitHub Actions for AI Quality.**

The goal is to make AI quality:

- measurable
- reproducible
- versioned
- continuously enforced

across development, CI/CD, and production.

---

## 🤝 Contributing

Contributions are welcome.

Whether you're interested in:

- AI Infrastructure
- AI Evaluation
- Backend Engineering
- Developer Tooling
- Clean Architecture

feel free to open an issue or submit a pull request.

---

## 📜 License

Apache License 2.0

---

<div align="center">

### ⭐ If you find OpenEval interesting, consider giving the repository a star.

**Building reliable AI systems starts with measurable quality.**

</div>