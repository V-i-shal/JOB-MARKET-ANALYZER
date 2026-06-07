# Job Market Analyzer
**AI-Powered Resume Analysis & Career Intelligence Tool**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-success.svg)]()
[![spaCy](https://img.shields.io/badge/NLP-spaCy-09A3D5.svg)](https://spacy.io/)
[![sklearn](https://img.shields.io/badge/ML-scikit--learn-F7931E.svg)](https://scikit-learn.org/)

---

## Overview

Job Market Analyzer is an end-to-end career intelligence pipeline that parses unstructured resumes, extracts skills using NLP, matches candidates to job roles via K-Means clustering, and generates personalised 4-week learning roadmaps — all in under **0.03 seconds per resume**.

Built as a portfolio project demonstrating applied NLP, unsupervised ML, and full-stack data engineering.

---

## Evaluation Metrics

Benchmarked against **50 diverse resumes** spanning Frontend, Backend, Data Science, and other engineering roles.

| Metric | Score | Method |
|---|---|---|
| **Skill Extraction Precision** | **100%** | Labeled ground-truth benchmark |
| **Skill Extraction Recall** | **84.58%** | Labeled ground-truth benchmark |
| **Skill Extraction F1-Score** | **90.26%** | Harmonic mean of Precision & Recall |
| **Avg Processing Time** | **<0.03s / resume** | Timed extraction across 50 resumes |
| **Silhouette Score (K=2)** | **0.2754** | sklearn silhouette_score on TF-IDF vectors |

> **Note on Precision:** The parser achieved zero false positives across all 50 resumes — meaning every extracted skill was a verified true positive. Recall of 84.6% reflects expected behaviour for a hybrid rule-based + NLP system on noisy unstructured text.

---

## Features

- **Multi-format Resume Parsing** — PDF and image (OCR via Tesseract) support
- **Hybrid NLP Skill Extraction** — spaCy + regex achieving 90.26% F1-Score across 50 resumes
- **K-Means Career Clustering** — Groups job roles into career tracks for targeted matching
- **Personalised Learning Paths** — Auto-generated 4-week plans mapped to identified skill gaps
- **Interactive Visualisations** — Plotly charts for skill gap analysis and job match distribution
- **Persistent Storage** — SQLite database with 34+ curated courses
- **Modern GUI** — CustomTkinter desktop interface + CLI mode

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| NLP | spaCy (en_core_web_sm) |
| Machine Learning | scikit-learn (K-Means, TF-IDF) |
| PDF Processing | pdfplumber |
| OCR | Tesseract |
| Visualisation | Plotly |
| Backend API | Flask |
| Database | SQLite |
| GUI | CustomTkinter |

---

## How It Works

```
Resume (PDF/Image)
       ↓
  Text Extraction          ← pdfplumber / Tesseract OCR
       ↓
  Skill Extraction         ← spaCy NLP + regex (100% Precision, 90.26% F1)
       ↓
  Job Fetching             ← 200+ curated job role database
       ↓
  K-Means Clustering       ← Career track matching (Silhouette: 0.2754)
       ↓
  Skill Gap Analysis       ← Missing skills identified per role
       ↓
  Learning Path Generator  ← Personalised 4-week roadmap
       ↓
  Plotly Dashboard         ← Interactive visualisations
```

---

## Installation

**Prerequisites:** Python 3.10+, pip, Tesseract OCR (optional, for image resumes)

```bash
# Clone the repository
git clone https://github.com/V-i-shal/job-market-analyzer.git
cd job-market-analyzer

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

---

## Usage

```bash
# GUI Mode
python main.py

# CLI Mode
python main.py --mode cli path/to/resume.pdf --domain "Data Scientist" --jobs 20
```

---

## Project Structure

```
job-market-analyzer/
├── src/
│   ├── models/          # Data structures (Resume, AnalysisResult)
│   ├── services/        # Core pipeline (parser, extractor, analyzer)
│   ├── utils/           # File validator, chart generator
│   └── gui/             # CustomTkinter interface
├── data/                # SQLite database
├── tests/               # Unit and service tests
├── logs/                # Application logs
├── main.py              # Entry point
└── requirements.txt
```

---

## Author

**Vishal Deep N D**
- GitHub: [github.com/V-i-shal](https://github.com/V-i-shal)
- LinkedIn: [linkedin.com/in/vishaldeepnd](https://linkedin.com/in/vishaldeepnd)