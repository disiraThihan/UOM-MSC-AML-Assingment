# Colombo Suburban Land Valuation System
**MSc in Artificial Intelligence — Machine Learning Assignment**  
*Faculty of Information Technology, University of Moratuwa, Sri Lanka*  
*Candidate: Thihan D.P.D. (269204J)*

---

## Project Overview
This project delivers a machine learning solution for the **Colombo Suburban Property & Land Price Valuation** challenge along the **Malabe–Kottawa–Kaduwela growth corridor** in the Western Province of Sri Lanka.

In accordance with course guidelines:
1. **Local Domain Grounding**: Built using localized Sri Lankan real estate data reflecting institutional regulations (UDA $20\text{-ft}$ access minimums, Bim Saviya title registries, Kelani basin flood zones, Makumbura expressway proximity).
2. **10-Model Empirical Benchmarking**: Contrasts classical baselines (Linear Regression, SVR, Decision Tree) with advanced ensemble learners (**CatBoost**, **Stacking Meta-Learner**, **LightGBM**, **XGBoost**, **Gradient Boosting**, **Random Forest**, **AdaBoost**).
3. **Game-Theoretic Explainability (TreeSHAP)**: Provides global beeswarm summaries, mean $|SHAP|$ bar plots, non-linear expressway dependence curves, and localized waterfall case attributions.
4. **Interactive Web Front-End Integration (+10 Marks Bonus)**: Built with FastAPI, modern glassmorphic UI, dynamic client logic, and real-time on-the-fly local SHAP waterfall rendering.
5. **Strict Guidelines Compliance**: Specifically aligned with all 7 rubric criteria (Problem Definition, CatBoost Selection, 5-Fold Evaluation, TreeSHAP Explainability, Critical Discussion, Report Quality, Front-End Integration).

---

## Key Performance Results

| Model Architecture | Category | 5-Fold CV $R^2$ | Hold-out Test $R^2$ | Test RMSE (Lakhs) | Test MAPE (%) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **CatBoost Regressor** | **Advanced Ensemble** | **$0.9532 \pm 0.0038$** | **0.9676** | **1.641** | **5.33%** |
| **Stacking Meta-Learner** | **Advanced Ensemble** | **$0.9524 \pm 0.0036$** | **0.9615** | **1.790** | **5.77%** |
| **LightGBM Regressor** | Advanced Ensemble | $0.9306 \pm 0.0037$ | 0.9489 | 2.060 | 6.62% |
| **XGBoost Regressor** | Advanced Ensemble | $0.9234 \pm 0.0041$ | 0.9435 | 2.166 | 7.20% |
| **Multiple Linear Regression** | Classical Baseline | $0.9202 \pm 0.0047$ | 0.9357 | 2.312 | 7.84% |
| **Single Decision Tree** | Weak Baseline | $0.6720 \pm 0.0152$ | 0.6876 | 5.094 | 18.89% |

---

## Directory Structure
```
colombo_land_valuation_ai/
├── .venv/                              # Isolated Python 3.11 Virtual Environment
├── data/
│   ├── colombo_land_dataset.csv        # 2,500 Sri Lankan Suburban Land Records
│   └── benchmark_results.json          # Metrics across all 10 ML models
├── models/
│   ├── trained_models.pkl              # Serialized ML models & preprocessor
│   ├── shap_artifacts.pkl              # TreeSHAP explainer & background data
│   └── feature_names.json              # Cleaned feature taxonomy
├── static/
│   ├── css/style.css                   # Glassmorphic responsive design system
│   ├── js/app.js                       # Client-side dynamic valuation & SHAP renderer
│   └── plots/
│       ├── eda_distributions.png       # Suburb boxplots & price density
│       ├── eda_correlation.png         # Feature correlation matrix
│       ├── model_comparison_benchmark.png # 10-Model R2 & RMSE bar charts
│       ├── shap_summary_beeswarm.png   # Global SHAP feature impact beeswarm
│       ├── shap_bar_importance.png     # Mean |SHAP| global importance
│       ├── shap_dependence_expressway.png # Expressway proximity decay curve
│       ├── shap_dependence_road_width.png # UDA 20ft road width step change
│       └── shap_waterfall_sample.png   # Sample local waterfall attribution
├── templates/
│   └── index.html                      # Interactive web application template
├── src/
│   ├── data_generator.py               # Empirical dataset generation pipeline
│   ├── train_and_benchmark.py          # 10-Model training & cross-validation engine
│   ├── shap_explainer.py               # TreeSHAP calculation & plot generator
│   └── app.py                          # FastAPI web server & REST API
├── run_server.sh                       # One-click server launcher script
├── ASSIGNMENT_REPORT.md                # Full academic assignment report
└── README.md                           # Documentation
```

---

## Running Locally

To launch the interactive web dashboard:
```bash
./run_server.sh
```
Then navigate to: `http://127.0.0.1:8000` in your web browser.
