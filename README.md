<div align="center">

# 🚀 OpenEval

### CI/CD and Production Quality Platform for LLM Applications

*Building reproducible, versioned, and continuously evaluated AI systems.*

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-Apache%202.0-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active%20Development-orange?style=for-the-badge)

</div>

---

# 📖 Overview

OpenEval is an open-source evaluation platform for **Large Language Model (LLM) applications**.

The goal of OpenEval is to make AI quality:

- **Reproducible**
- **Versioned**
- **Comparable**
- **Continuously Evaluated**

Rather than treating evaluation as a one-time experiment, OpenEval integrates evaluation into the software development lifecycle, making it possible to evaluate AI systems consistently during development, CI/CD, and production.

---

# ❓ Why OpenEval?

Traditional software has:

- Unit Tests
- Integration Tests
- CI/CD Pipelines

Modern AI systems also need continuous quality checks.

OpenEval aims to provide a framework where AI evaluation becomes as natural as software testing.

Instead of asking:

> "Did the model perform well?"

OpenEval helps answer:

> "Can we continuously measure and enforce AI quality?"

---

# ✨ Current Features

- ✅ YAML-driven evaluation configuration
- ✅ Command-line interface (CLI)
- ✅ Clean Architecture
- ✅ Domain-Driven Design (DDD)
- ✅ Evaluation Definition workflow
- ✅ Run creation workflow
- ✅ GitHub Actions CI
- ✅ Extensible project structure

---

# 🏗 Architecture

OpenEval follows **Clean Architecture**, keeping business logic independent of frameworks and infrastructure.

```text
             Interface
        (CLI / REST / GitHub)

                 │
                 ▼

            Application
            (Use Cases)

                 │
                 ▼

              Domain
      (Business Rules & Models)

                 │
                 ▼

          Infrastructure
(Database • Providers • Plugins)
```

Dependencies always point inward.

---

# 📂 Project Structure

```text
OpenEval/
│
├── .github/
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

# ⚙️ Current Workflow

The current workflow is:

```text
evaluation.yaml
        │
        ▼
 Load Configuration
        │
        ▼
Create Evaluation Definition
        │
        ▼
      Create Run
        │
        ▼
   Display Summary
```

---

# 🚀 Quick Start

## Clone the repository

```bash
git clone https://github.com/Harshrudrawar/OpenEval.git
cd OpenEval
```

## Install

```bash
pip install -e .
```

## Run the example

```bash
python -m openeval.interface.cli run examples/basic/evaluation.yaml
```

Example output:

```text
✔ Evaluation created successfully

ID: 83be7e45-e527-4f57-802b-53d17b037ad4
Name: Demo Evaluation
Dataset Version: dataset-v1
Prompt Version: prompt-v1
Metrics: 1

Run created successfully

Run ID: d8c5f61c-338a-4d07-b204-35d31c7e1088
Run Status: created
```

---

# 📄 Example Configuration

```yaml
name: Demo Evaluation

dataset:
  version: dataset-v1

prompt:
  version: prompt-v1

target:
  provider: openai
  model: gpt-4o

metrics:
  - accuracy
```

---

# 🛣 Roadmap

## Phase 1 — Foundation ✅

- [x] Clean Architecture
- [x] Domain Layer
- [x] Application Layer
- [x] Infrastructure Layer
- [x] YAML Configuration
- [x] CLI
- [x] Evaluation Creation
- [x] Run Creation
- [x] GitHub Actions

---

## Phase 2 — Evaluation Engine 🚧

- [ ] Dataset Loading
- [ ] Prompt Loading
- [ ] Case Generation
- [ ] Evaluation Execution
- [ ] Run Lifecycle

---

## Phase 3 — Metrics

- [ ] Accuracy
- [ ] BLEU
- [ ] ROUGE
- [ ] LLM-as-a-Judge
- [ ] Custom Metric Plugins

---

## Phase 4 — Reports

- [ ] HTML Reports
- [ ] Run History
- [ ] Baseline Comparison
- [ ] Trend Analysis

---

## Phase 5 — Production

- [ ] PostgreSQL Support
- [ ] REST API
- [ ] GitHub Action
- [ ] Docker Support
- [ ] Plugin Marketplace

---

# 🎯 Design Principles

OpenEval is built around a few core principles:

- Version everything.
- Reproduce everything.
- Keep business logic framework-independent.
- Prefer explicit domain models.
- Design for extensibility.
- Build features as vertical slices.

---

# 🤝 Contributing

Contributions are welcome.

Whether you're interested in:

- AI Evaluation
- AI Infrastructure
- Backend Engineering
- Clean Architecture
- Developer Tooling

feel free to open an issue or submit a pull request.

---

# 📜 License

Licensed under the Apache 2.0 License.

---

<div align="center">

**Building reliable AI systems starts with measurable quality.**

⭐ If you find OpenEval useful, consider giving the project a star.

</div>