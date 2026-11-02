"""
Explainable AI (XAI) Engine using TreeSHAP
Generates Global Interpretability (Beeswarm, Mean |SHAP| Bar, Dependence Plots)
and Local Interpretability (Waterfall Plots, Force Plots) for Colombo Land Valuation.
"""

import os
import joblib
import numpy as np
import pandas as pd
import shap
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLOTS_DIR = os.path.join(BASE_DIR, "static", "plots")
MODELS_DIR = os.path.join(BASE_DIR, "models")

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Helvetica'

def clean_feature_name(name):
    """Makes one-hot and raw feature names human-readable for academic charts and UI."""
    if "locality_" in name:
        return f"Locality: {name.split('locality_')[-1].replace('_', ' ')}"
    if "zoning_type_" in name:
        return f"Zoning: {name.split('zoning_type_')[-1].replace('_', ' ')}"
    if "deed_type_" in name:
        return f"Deed: {name.split('deed_type_')[-1].replace('_', ' ')}"
    if "road_type_" in name:
        return f"Road Surface: {name.split('road_type_')[-1].replace('_', ' ')}"
    if "topography_" in name:
        return f"Topography: {name.split('topography_')[-1].replace('_', ' ')}"
    if "flood_risk_level_" in name:
        val = name.split('flood_risk_level_')[-1]
        return f"Flood Hazard: {val}" if val != 'nan' else "Flood Hazard: Baseline"
    if "shape_regularity_" in name:
        return f"Plot Shape: {name.split('shape_regularity_')[-1].replace('_', ' ')}"

    name = name.replace("num__", "")
    mapping = {
        "dist_expressway_interchange_km": "Dist. to Expressway (km)",
        "dist_colombo_cbd_km": "Dist. to Colombo CBD (km)",
        "dist_nearest_university_km": "Dist. to University / IT Park (km)",
        "dist_main_bus_route_m": "Dist. to Main Bus Route (m)",
        "road_width_ft": "Road Width (ft)",
        "perch_size": "Plot Extent (Perches)",
        "pipe_water_available": "Pipe Water Access",
        "three_phase_electricity": "3-Phase Electricity",
        "facing_road_frontage_ft": "Road Frontage (ft)"
    }
    return mapping.get(name, name.replace("_", " "))


def run_shap_analysis():
    artifacts_path = os.path.join(MODELS_DIR, "trained_models.pkl")
    if not os.path.exists(artifacts_path):
        raise FileNotFoundError(f"Model artifacts not found at {artifacts_path}. Run training first!")

    artifacts = joblib.load(artifacts_path)
    models = artifacts["models"]
    raw_feature_names = artifacts["all_feature_names"]
    human_feature_names = [clean_feature_name(f) for f in raw_feature_names]

    X_train = artifacts["X_train"]
    X_test = artifacts["X_test"]
    y_test = artifacts["y_test"]

    # Select best tree ensemble for TreeSHAP
    # XGBoost or CatBoost or LightGBM
    if "CatBoost" in models:
        explainer_model = models["CatBoost"]
        model_type_name = "CatBoost Regressor"
    elif "XGBoost" in models:
        explainer_model = models["XGBoost"]
        model_type_name = "XGBoost Regressor"
    else:
        explainer_model = models["Random Forest (Bagging)"]
        model_type_name = "Random Forest"

    print(f"Building TreeSHAP Explainer for {model_type_name}...")
    explainer = shap.TreeExplainer(explainer_model)
    shap_values = explainer(X_test)

    # Replace feature names with clean labels
    shap_values.feature_names = human_feature_names

    # 1. SHAP Summary Beeswarm Plot
    print("Generating SHAP Summary (Beeswarm) Plot...")
    plt.figure(figsize=(12, 8))
    shap.plots.beeswarm(shap_values, max_display=15, show=False)
    plt.title(f"SHAP Global Feature Impact (Beeswarm): Colombo Suburban Land Pricing ({model_type_name})", fontsize=12, fontweight='bold', pad=12)
    plt.tight_layout()
    beeswarm_path = os.path.join(PLOTS_DIR, "shap_summary_beeswarm.png")
    plt.savefig(beeswarm_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved beeswarm plot to {beeswarm_path}")

    # 2. SHAP Global Feature Importance Bar Plot
    print("Generating SHAP Feature Importance Bar Plot...")
    plt.figure(figsize=(10, 7))
    shap.plots.bar(shap_values, max_display=15, show=False)
    plt.title(f"Mean |SHAP Value| (Global Feature Importance): {model_type_name}", fontsize=12, fontweight='bold', pad=12)
    plt.tight_layout()
    bar_path = os.path.join(PLOTS_DIR, "shap_bar_importance.png")
    plt.savefig(bar_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved bar importance plot to {bar_path}")

    # 3. SHAP Dependence Plot: Expressway Proximity
    print("Generating SHAP Dependence Plot for Expressway Proximity...")
    plt.figure(figsize=(10, 6))
    exp_idx = [i for i, name in enumerate(human_feature_names) if "Expressway" in name][0]
    shap.plots.scatter(shap_values[:, exp_idx], show=False)
    plt.title("SHAP Non-Linear Dependence: Distance to Expressway Interchange vs Valuation Impact", fontsize=12, fontweight='bold', pad=12)
    plt.xlabel("Distance to Nearest Expressway Interchange (km)", fontsize=11, fontweight='bold')
    plt.ylabel("SHAP Value (Impact on LKR Lakhs/Perch)", fontsize=11, fontweight='bold')
    plt.tight_layout()
    dep_path = os.path.join(PLOTS_DIR, "shap_dependence_expressway.png")
    plt.savefig(dep_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved expressway dependence plot to {dep_path}")

    # 4. SHAP Dependence Plot: Road Width (UDA 20ft regulation effect)
    print("Generating SHAP Dependence Plot for Road Width...")
    plt.figure(figsize=(10, 6))
    road_idx = [i for i, name in enumerate(human_feature_names) if "Road Width" in name][0]
    shap.plots.scatter(shap_values[:, road_idx], show=False)
    plt.title("SHAP Non-Linear Dependence: Road Width (ft) vs Valuation Impact (UDA Regulations)", fontsize=12, fontweight='bold', pad=12)
    plt.xlabel("Access Road Width (feet)", fontsize=11, fontweight='bold')
    plt.ylabel("SHAP Value (Impact on LKR Lakhs/Perch)", fontsize=11, fontweight='bold')
    plt.tight_layout()
    road_dep_path = os.path.join(PLOTS_DIR, "shap_dependence_road_width.png")
    plt.savefig(road_dep_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved road width dependence plot to {road_dep_path}")

    # 5. Local Explanation: Waterfall Plot for a representative property
    # Let's find a prime Malabe or Kottawa property in test set
    print("Generating Local Waterfall Explanation...")
    # Find a sample where actual price is high
    sample_idx = int(np.argmax(y_test.values))
    plt.figure(figsize=(11, 7))
    shap.plots.waterfall(shap_values[sample_idx], max_display=12, show=False)
    plt.title(f"SHAP Local Waterfall Explanation: High-Value Suburban Land Case (Sample #{sample_idx})", fontsize=12, fontweight='bold', pad=12)
    plt.tight_layout()
    waterfall_path = os.path.join(PLOTS_DIR, "shap_waterfall_sample.png")
    plt.savefig(waterfall_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved local waterfall plot to {waterfall_path}")

    # Save explainer artifacts for web deployment
    shap_deployment_bundle = {
        "explainer": explainer,
        "explainer_model_name": model_type_name,
        "expected_value": float(explainer.expected_value) if np.isscalar(explainer.expected_value) else float(explainer.expected_value[0]),
        "feature_names": raw_feature_names,
        "human_feature_names": human_feature_names
    }
    shap_bundle_path = os.path.join(MODELS_DIR, "shap_artifacts.pkl")
    joblib.dump(shap_deployment_bundle, shap_bundle_path)
    print(f"Saved SHAP deployment bundle to {shap_bundle_path}")

if __name__ == "__main__":
    run_shap_analysis()
