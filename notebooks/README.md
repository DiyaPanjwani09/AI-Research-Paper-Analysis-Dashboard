# Research Paper Intelligence Engine - Training Notebooks

This directory contains Jupyter notebooks for training various ML models.

## Notebooks

1. **data_preprocessing.ipynb** - Dataset preprocessing and cleaning
2. **summarization_training.ipynb** - Training summarization models
3. **similarity_search.ipynb** - Training similarity search models
4. **topic_modeling.ipynb** - Training topic models
5. **gap_detection.ipynb** - Training gap detection models
6. **analytics_models.ipynb** - Training analytics and forecasting models

## Usage

Run the notebooks in order to:
1. Preprocess the SciTLDR and arXiv datasets
2. Train summarization models using SciBERT
3. Build vector similarity search with Sentence Transformers
4. Train topic models with BERTopic
5. Train gap detection models
6. Train trend forecasting models

## Quick Start

```bash
# Install Jupyter
pip install jupyter

# Run notebooks
jupyter notebook notebooks/
```

## Notebook Details

### 1. Data Preprocessing
- Load and clean SciTLDR dataset
- Load and clean arXiv dataset
- Create training/evaluation splits

### 2. Summarization Training
- Load SciBERT model
- Fine-tune on SciTLDR dataset
- Evaluate summarization quality

### 3. Similarity Search
- Generate embeddings with Sentence Transformers
- Build FAISS index
- Evaluate similarity search quality

### 4. Topic Modeling
- Train BERTopic model
- Train LDA model
- Evaluate topic coherence

### 5. Gap Detection
- Extract limitation patterns
- Train classification model
- Evaluate gap detection accuracy

### 6. Analytics Models
- Train trend forecasting models
- Evaluate prediction accuracy
- Generate analytics visualizations