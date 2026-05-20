# ManBert

AI-assisted manuscript detection framework for analyzing the adoption of generative AI in academic writing.

## Overview

ManBert is a hybrid AI manuscript detection system designed to identify AI-assisted scientific writing in full research papers. The project combines a BERT-based classifier with manually engineered linguistic and structural features to detect AI-generated or AI-assisted academic manuscripts.

The framework was developed to study the growth of AI-assisted writing across scholarly publications between 2021 and 2025 using approximately one million full-text journal articles.

Based on the associated research paper, the model achieves an F1 score of 0.95, outperforming several existing AI detection systems including GPTZero, ZeroGPT, Sapling AI, and standalone BERT baselines.

---

## Key Features

- Hybrid architecture combining:
  - BERT embeddings
  - Manual AI-writing feature extraction
  - Deep neural network classifier
- Full-manuscript AI detection
- Detection of mixed human + AI authored content
- Trained on diverse LLM-generated samples
- Longitudinal analysis support for publication trends
- Scalable pipeline for large-scale manuscript screening

---

## Model Architecture

Input Manuscript
        │
        ▼
Text Extraction
        │
 ┌───────────────┬────────────────┐
 ▼               ▼
BERT Encoder   Manual Feature Extraction
 │               │
 └──────┬────────┘
        ▼
 Feature Concatenation
        ▼
 Deep Neural Network
 (32 → 16 hidden layers)
        ▼
 Sigmoid Output
        ▼
 AI / Non-AI Classification

---

## Dataset

### Training Set Composition

| Category | Samples |
|---|---|
| AI-generated manuscripts | 512 |
| Non-AI manuscripts (2006 papers) | 512 |
| Total | 1024 |

### AI Sources Used

Generated content includes outputs from:
- ChatGPT
- Gemini
- Claude
- Copilot
- DeepSeek
- Mistral
- Grok
- Perplexity

Dataset split:
- 80% Training
- 10% Validation
- 10% Testing

---

## Performance Comparison

| Method | F1 Score |
|---|---|
| ManBert | 0.95 |
| GPTZero | 0.82 |
| BERT baseline | 0.78 |
| Sapling AI | 0.73 |
| ZeroGPT | 0.70 |

---

## Repository Structure

ManBert/
├── data/
├── models/
├── scripts/
├── notebooks/
├── results/
├── figures/
├── requirements.txt
└── README.md

---

## Installation

```bash
git clone https://github.com/lorewar2/ManBert.git

cd ManBert

pip install -r requirements.txt
```

---

## Usage

### Train Model

```bash
python train.py
```

### Run Inference

```bash
python infer.py --input manuscript.pdf
```

### Evaluate

```bash
python evaluate.py
```

---

## Applications

- Scholarly publishing research
- AI-assisted writing analysis
- Academic integrity studies
- Bibliometric research
- LLM adoption tracking
- Scientific writing analytics

---

## Authors

- Minindu Weerakoon
- Bavindhu Amarathunga
- Pamodya Weerasuriya
- Pathmanathan Sivashankar

Auburn University

---

## License

This project is intended for research and educational purposes.
