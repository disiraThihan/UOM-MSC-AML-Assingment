"""
Model Training, Cross-Validation Benchmarking, and EDA Generation
Compares Classical Baselines (Linear Regression, SVR, Decision Tree)
against Modern Ensemble Learners (Random Forest, AdaBoost, Gradient Boosting,
LightGBM, XGBoost, CatBoost, and Stacking Meta-Learner).
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error, mean_absolute_percentage_error

# Classical Baselines
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor

# Advanced Ensemble Learners
from sklearn.ensemble import RandomForestRegressor, AdaBoostRegressor, GradientBoostingRegressor, StackingRegressor
from lightgbm import LGBMRegressor
from xgboost import XGBRegressor
from catboost import CatBoostRegressor

# Matplotlib visual settings
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Helvetica'
plt.rcParams['axes.edgecolor'] = '#cbd5e1'
plt.rcParams['axes.linewidth'] = 0.8

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "colombo_land_dataset.csv")
PLOTS_DIR = os.path.join(BASE_DIR, "static", "plots")
MODELS_DIR = os.path.join(BASE_DIR, "models")

os.makedirs(PLOTS_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

def generate_eda_visualizations(df):
    print("Generating EDA Visualizations...")

    # 1. Price Distributions & Suburb Boxplots
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # Suburb Perch Price Boxplot
    order = df.groupby("locality")["price_per_perch_lkr_lakhs"].median().sort_values(ascending=False).index
    palette = sns.color_palette("mako", len(order))
    sns.boxplot(data=df, x="locality", y="price_per_perch_lkr_lakhs", order=order, ax=axes[0], palette=palette)
    axes[0].set_title("Land Price Distribution across Colombo Suburbs (LKR Lakhs/Perch)", fontsize=13, fontweight='bold', pad=10)
    axes[0].set_xlabel("Locality", fontsize=11, fontweight='bold')
    axes[0].set_ylabel("Price per Perch (LKR Lakhs)", fontsize=11, fontweight='bold')
    axes[0].tick_params(axis='x', rotation=35)

    # Price Histogram with KDE
    sns.histplot(df["price_per_perch_lkr_lakhs"], kde=True, ax=axes[1], color="#2563eb", bins=30, line_kws={"linewidth": 2})
    axes[1].axvline(df["price_per_perch_lkr_lakhs"].mean(), color="#dc2626", linestyle="--", label=f"Mean: {df['price_per_perch_lkr_lakhs'].mean():.2f} Lakhs")
    axes[1].axvline(df["price_per_perch_lkr_lakhs"].median(), color="#16a34a", linestyle="-", label=f"Median: {df['price_per_perch_lkr_lakhs'].median():.2f} Lakhs")
    axes[1].set_title("Overall Land Price Density (Colombo Suburban Corridor)", fontsize=13, fontweight='bold', pad=10)
    axes[1].set_xlabel("Price per Perch (LKR Lakhs)", fontsize=11, fontweight='bold')
    axes[1].set_ylabel("Frequency", fontsize=11, fontweight='bold')
    axes[1].legend(frameon=True, facecolor='white', framealpha=0.9)

    plt.tight_layout()
    dist_plot_path = os.path.join(PLOTS_DIR, "eda_distributions.png")
    plt.savefig(dist_plot_path, dpi=300)
    plt.close()
    print(f"Saved distribution plot to {dist_plot_path}")

    # 2. Correlation Matrix of Numerical Features
    num_cols = [
        "perch_size", "dist_expressway_interchange_km", "dist_colombo_cbd_km",
        "dist_nearest_university_km", "dist_main_bus_route_m", "road_width_ft",
        "facing_road_frontage_ft", "price_per_perch_lkr_lakhs"
    ]
    plt.figure(figsize=(10, 8))
    corr = df[num_cols].corr()
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(
        corr, mask=mask, annot=True, fmt=".2f", cmap="vlag", vmin=-1, vmax=1,
        square=True, linewidths=0.5, cbar_kws={"shrink": 0.8}
    )
    plt.title("Correlation Heatmap: Colombo Suburban Land Attributes & Valuation", fontsize=13, fontweight='bold', pad=12)
    plt.tight_layout()
    corr_plot_path = os.path.join(PLOTS_DIR, "eda_correlation.png")
    plt.savefig(corr_plot_path, dpi=300)
    plt.close()
    print(f"Saved correlation plot to {corr_plot_path}")

def run_benchmarking():
    df = pd.read_csv(DATA_PATH)
    generate_eda_visualizations(df)

    # Feature definitions
    cat_features = [
        "locality", "road_type", "zoning_type", "deed_type",
        "topography", "flood_risk_level", "shape_regularity"
    ]
    num_features = [
        "perch_size", "dist_expressway_interchange_km", "dist_colombo_cbd_km",
        "dist_nearest_university_km", "dist_main_bus_route_m", "road_width_ft",
        "pipe_water_available", "three_phase_electricity", "facing_road_frontage_ft"
    ]

    target = "price_per_perch_lkr_lakhs"

    X = df[cat_features + num_features]
    y = df[target]

    # Preprocessing
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(drop="first", sparse_output=False, handle_unknown="ignore"), cat_features),
            ("num", StandardScaler(), num_features)
        ],
        remainder="passthrough"
    )

    X_processed = preprocessor.fit_transform(X)
    cat_encoded_names = preprocessor.named_transformers_["cat"].get_feature_names_out(cat_features).tolist()
    all_feature_names = cat_encoded_names + num_features

    # Train / Test split (80/20)
    X_train, X_test, y_train, y_test = train_test_split(
        X_processed, y, test_size=0.20, random_state=42
    )

    print(f"Processed feature matrix: {X_train.shape[1]} features, {X_train.shape[0]} train rows, {X_test.shape[0]} test rows.")

    # Model Dictionary (Baselines vs Ensembles)
    models = {
        # Baseline Models (lecturer said to avoid using simple models alone)
        "Linear Regression (Baseline)": LinearRegression(),
        "Support Vector Regressor (SVR)": SVR(C=50.0, epsilon=0.2, kernel="rbf"),
        "Decision Tree": DecisionTreeRegressor(max_depth=6, random_state=42),

        # Advanced Ensemble Learners
        "Random Forest (Bagging)": RandomForestRegressor(n_estimators=250, max_depth=14, random_state=42, n_jobs=-1),
        "AdaBoost Regressor": AdaBoostRegressor(n_estimators=150, learning_rate=0.08, random_state=42),
        "Gradient Boosting (GBM)": GradientBoostingRegressor(n_estimators=200, learning_rate=0.06, max_depth=5, random_state=42),
        "LightGBM": LGBMRegressor(n_estimators=250, learning_rate=0.05, num_leaves=31, random_state=42, verbose=-1),
        "XGBoost": XGBRegressor(n_estimators=250, learning_rate=0.05, max_depth=6, subsample=0.85, colsample_bytree=0.85, random_state=42, n_jobs=-1),
        "CatBoost": CatBoostRegressor(iterations=350, learning_rate=0.06, depth=6, random_seed=42, verbose=0)
    }

    # Stacking Ensemble combining top gradient boosters
    estimators = [
        ('xgb', XGBRegressor(n_estimators=200, learning_rate=0.05, max_depth=5, random_state=42, n_jobs=-1)),
        ('lgb', LGBMRegressor(n_estimators=200, learning_rate=0.05, num_leaves=25, random_state=42, verbose=-1)),
        ('cat', CatBoostRegressor(iterations=250, learning_rate=0.06, depth=5, random_seed=42, verbose=0)),
        ('rf', RandomForestRegressor(n_estimators=150, max_depth=12, random_state=42, n_jobs=-1))
    ]
    stacking_reg = StackingRegressor(
        estimators=estimators,
        final_estimator=Ridge(alpha=1.0),
        cv=5,
        n_jobs=-1
    )
    models["Stacking Meta-Learner (Ensemble)"] = stacking_reg

    # 5-Fold Cross Validation & Evaluation
    benchmark_results = []
    trained_model_instances = {}

    kf = KFold(n_splits=5, shuffle=True, random_state=42)

    print("\n--- Starting Model Benchmarking (5-Fold CV + Test Set) ---")
    for name, model in models.items():
        print(f"Training: {name} ...")
        # 5-fold CV R2 on training set
        cv_scores = cross_val_score(model, X_train, y_train, cv=kf, scoring="r2", n_jobs=-1)
        mean_cv_r2 = float(np.mean(cv_scores))
        std_cv_r2 = float(np.std(cv_scores))

        # Train on full train set
        model.fit(X_train, y_train)
        trained_model_instances[name] = model

        # Evaluate on hold-out test set
        y_pred = model.predict(X_test)
        test_r2 = float(r2_score(y_test, y_pred))
        test_rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
        test_mae = float(mean_absolute_error(y_test, y_pred))
        test_mape = float(mean_absolute_percentage_error(y_test, y_pred) * 100.0)

        is_ensemble = "Ensemble" in name or "Boost" in name or "Forest" in name or "Stacking" in name

        benchmark_results.append({
            "model_name": name,
            "category": "Advanced Ensemble" if is_ensemble else "Baseline",
            "cv_r2_mean": round(mean_cv_r2, 4),
            "cv_r2_std": round(std_cv_r2, 4),
            "test_r2": round(test_r2, 4),
            "test_rmse": round(test_rmse, 3),
            "test_mae": round(test_mae, 3),
            "test_mape": round(test_mape, 2)
        })

        print(f"  -> Test R2: {test_r2:.4f} | RMSE: {test_rmse:.3f} Lakhs | MAE: {test_mae:.3f} Lakhs | MAPE: {test_mape:.2f}%")

    # Sort results by Test R2 descending
    benchmark_results = sorted(benchmark_results, key=lambda x: x["test_r2"], reverse=True)

    # Save benchmark JSON
    benchmark_json_path = os.path.join(BASE_DIR, "data", "benchmark_results.json")
    with open(benchmark_json_path, "w") as f:
        json.dump(benchmark_results, f, indent=4)
    print(f"\nSaved benchmark results to {benchmark_json_path}")

    # Plot Model Comparison Benchmark Chart
    plot_model_comparison(benchmark_results)

    # Save trained objects
    artifacts = {
        "preprocessor": preprocessor,
        "all_feature_names": all_feature_names,
        "cat_features": cat_features,
        "num_features": num_features,
        "models": trained_model_instances,
        "best_model_name": benchmark_results[0]["model_name"],
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test
    }
    model_artifacts_path = os.path.join(MODELS_DIR, "trained_models.pkl")
    joblib.dump(artifacts, model_artifacts_path)
    print(f"Serialized trained artifacts to {model_artifacts_path}")

    # Feature names metadata
    with open(os.path.join(MODELS_DIR, "feature_names.json"), "w") as f:
        json.dump({"features": all_feature_names, "best_model": benchmark_results[0]["model_name"]}, f, indent=4)

    return benchmark_results

def plot_model_comparison(results):
    df_res = pd.DataFrame(results)

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    # 1. R2 Score Comparison
    colors = ['#059669' if cat == 'Advanced Ensemble' else '#dc2626' for cat in df_res['category']]
    bars1 = axes[0].barh(df_res['model_name'], df_res['test_r2'], color=colors, edgecolor='#1e293b', height=0.65)
    axes[0].set_xlim(0, 1.0)
    axes[0].set_xlabel("Hold-out Test $R^2$ Score", fontsize=11, fontweight='bold')
    axes[0].set_title("Variance Explained ($R^2$ Score): Ensembles vs. Baselines", fontsize=13, fontweight='bold', pad=10)
    axes[0].axvline(0.85, color='#475569', linestyle=':', label='High Performance Threshold (0.85)')

    # Add data labels
    for bar in bars1:
        w = bar.get_width()
        axes[0].text(w + 0.015, bar.get_y() + bar.get_height()/2, f"{w:.4f}", va='center', ha='left', fontsize=9, fontweight='bold')

    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#059669', label='Advanced Ensembles (Boosting / Stacking)'),
        Patch(facecolor='#dc2626', label='Classical Baselines (Linear / SVR / Single Tree)')
    ]
    axes[0].legend(handles=legend_elements, loc='lower right', frameon=True, facecolor='white')
    axes[0].invert_yaxis()

    # 2. RMSE Comparison (Lower is better)
    bars2 = axes[1].barh(df_res['model_name'], df_res['test_rmse'], color=colors, edgecolor='#1e293b', height=0.65)
    axes[1].set_xlabel("Root Mean Squared Error (LKR Lakhs/Perch)", fontsize=11, fontweight='bold')
    axes[1].set_title("Prediction Error (RMSE in Lakhs): Lower is Better", fontsize=13, fontweight='bold', pad=10)

    for bar in bars2:
        w = bar.get_width()
        axes[1].text(w + 0.05, bar.get_y() + bar.get_height()/2, f"{w:.2f}", va='center', ha='left', fontsize=9, fontweight='bold')

    axes[1].invert_yaxis()

    plt.suptitle("Sri Lanka Land Valuation: Algorithmic Benchmark across 10 Machine Learning Architectures", fontsize=15, fontweight='bold', y=0.98)
    plt.tight_layout()
    chart_path = os.path.join(PLOTS_DIR, "model_comparison_benchmark.png")
    plt.savefig(chart_path, dpi=300)
    plt.close()
    print(f"Saved model benchmark comparison plot to {chart_path}")

if __name__ == "__main__":
    run_benchmarking()
