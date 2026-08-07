<div align="center">

# 🚀 OpenEval

### Open-Source AI Evaluation Platform for LLM Applications

**Run evaluations. Compare models. Enforce AI Quality.**

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)]()
[![License](https://img.shields.io/badge/License-Apache%202.0-green?style=for-the-badge)]()
[![CI](https://github.com/Harshrudrawar/OpenEval/actions/workflows/ci.yml/badge.svg)](https://github.com/Harshrudrawar/OpenEval/actions/workflows/ci.yml)
[![Status](https://img.shields.io/badge/Status-Active%20Development-orange?style=for-the-badge)]()

</div>

---

# Why OpenEval?

Modern software has:

- Unit Tests
- Integration Tests
- CI/CD Pipelines

Modern AI applications deserve the same engineering discipline.

OpenEval is an open-source platform that brings **continuous evaluation** to LLM applications.

Instead of asking:

> "Did my model perform well?"

OpenEval helps answer:

> **"Can I continuously measure, compare, and enforce AI quality?"**

---

# Current Capabilities

Today OpenEval can:

- ✅ YAML-driven evaluations
- ✅ CSV dataset loading
- ✅ Case generation
- ✅ Evaluation pipeline
- ✅ Run creation
- ✅ Mock execution
- ✅ Ollama execution
- ✅ OpenAI provider architecture
- ✅ Accuracy metric
- ✅ Plugin architecture
- ✅ Clean Architecture
- ✅ GitHub Actions CI

---

# Current Workflow

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
 Execute Target
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

# Quick Start

## Clone

```bash
git clone https://github.com/Harshrudrawar/OpenEval.git
cd OpenEval
```

## Install

```bash
pip install -e .
```

## Run

```bash
python -m openeval.interface.cli run examples/basic/evaluation.yaml
```

Example Output

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

# Example Configuration

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

To use Ollama:

```yaml
target:
  provider: ollama
  model: llama3
```

To use OpenAI (coming soon):

```yaml
target:
  provider: openai
  model: gpt-4o
```

---

# Project Structure

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

# Architecture

OpenEval follows **Clean Architecture**.

```text
              Interface
          (CLI / API / GitHub)

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
 (Providers • Storage • Plugins)
```

Dependencies always point inward.

---

# Design Principles

OpenEval is built around a few core ideas.

- Version everything
- Reproduce everything
- Evaluate continuously
- Keep business logic framework-independent
- Build extensible plugin systems
- Prefer vertical slices over horizontal layers
- Keep the CI pipeline green

---

# Roadmap

## Completed

- [x] YAML configuration
- [x] Dataset loading
- [x] Case generation
- [x] Evaluation pipeline
- [x] Run creation
- [x] Mock provider
- [x] Ollama provider
- [x] OpenAI provider architecture
- [x] Accuracy metric
- [x] Plugin architecture
- [x] GitHub Actions
- [x] Ruff
- [x] Black
- [x] MyPy
- [x] Pytest

---

## Next

- [ ] Real OpenAI execution
- [ ] Model comparison
- [ ] HTML reports
- [ ] Cost tracking
- [ ] Latency tracking
- [ ] GitHub Action

---

## Future

- [ ] Claude support
- [ ] Gemini support
- [ ] Azure OpenAI
- [ ] LLM-as-a-Judge
- [ ] Experiment tracking
- [ ] Quality Gates
- [ ] Benchmarking Dashboard

---

# Long-Term Vision

OpenEval aims to become:

> **GitHub Actions for AI Quality.**

The goal is to make AI quality measurable, reproducible, and enforceable across development, CI/CD, and production.

---

# Contributing

Contributions are welcome.

Whether you're interested in:

- AI Infrastructure
- AI Evaluation
- Backend Engineering
- Clean Architecture
- Developer Tooling

feel free to open an issue or submit a pull request.

---

# License

Apache 2.0

---

<div align="center">

## ⭐ If OpenEval interests you, consider giving the repository a star.

**Building reliable AI systems starts with measurable quality.**

</div>