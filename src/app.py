"""
FastAPI Server & Deployment Engine for Colombo Suburban Land Valuation AI
Provides interactive REST API endpoints for property valuation and live local SHAP explanations.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, List
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from pydantic import BaseModel, Field

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")
DATA_DIR = os.path.join(BASE_DIR, "data")

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Colombo Suburban Land Valuation System",
    description="Tree Ensemble and Game-Theoretic SHAP Engine for Malabe-Kottawa Corridor",
    version="1.0.0"
)

# Enable CORS for GitHub Pages and external clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static and templates
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Global model state
state: Dict[str, Any] = {}

@app.on_event("startup")
def load_model_artifacts():
    print("Loading ML models and SHAP artifacts into memory...")
    artifacts_path = os.path.join(MODELS_DIR, "trained_models.pkl")
    shap_path = os.path.join(MODELS_DIR, "shap_artifacts.pkl")
    benchmarks_path = os.path.join(DATA_DIR, "benchmark_results.json")

    state["artifacts"] = joblib.load(artifacts_path)
    state["shap_bundle"] = joblib.load(shap_path)

    with open(benchmarks_path, "r") as f:
        state["benchmarks"] = json.load(f)

    state["preprocessor"] = state["artifacts"]["preprocessor"]
    state["models"] = state["artifacts"]["models"]
    state["best_model_name"] = state["artifacts"]["best_model_name"]
    state["best_model"] = state["models"][state["best_model_name"]]

    print(f"Server initialized with {state['best_model_name']} as primary inference engine.")

class PropertyValuationRequest(BaseModel):
    locality: str = Field(..., example="Malabe")
    perch_size: float = Field(..., ge=6.0, le=50.0, example=10.0)
    dist_expressway_interchange_km: float = Field(..., ge=0.1, le=15.0, example=2.5)
    dist_nearest_university_km: float = Field(..., ge=0.1, le=20.0, example=1.2)
    dist_main_bus_route_m: int = Field(..., ge=10, le=3000, example=200)
    road_width_ft: int = Field(..., ge=8, le=60, example=20)
    road_type: str = Field(..., example="Carpeted")
    zoning_type: str = Field(..., example="Residential_Medium")
    deed_type: str = Field(..., example="Bim_Saviya_First_Class")
    topography: str = Field(..., example="Flat_Elevated")
    flood_risk_level: str = Field(..., example="None")
    shape_regularity: str = Field(..., example="Rectangular")
    pipe_water_available: int = Field(1, ge=0, le=1)
    three_phase_electricity: int = Field(1, ge=0, le=1)

@app.get("/")
async def serve_dashboard():
    return FileResponse(os.path.join(BASE_DIR, "templates", "index.html"))

@app.get("/api/benchmark")
async def get_benchmarks():
    return JSONResponse(content=state.get("benchmarks", []))

@app.post("/api/predict")
async def predict_property_valuation(req: PropertyValuationRequest):
    # Form input dataframe
    row_data = {
        "locality": req.locality,
        "road_type": req.road_type,
        "zoning_type": req.zoning_type,
        "deed_type": req.deed_type,
        "topography": req.topography,
        "flood_risk_level": req.flood_risk_level,
        "shape_regularity": req.shape_regularity,
        "perch_size": req.perch_size,
        "dist_expressway_interchange_km": req.dist_expressway_interchange_km,
        "dist_colombo_cbd_km": 14.5, # baseline suburban distance
        "dist_nearest_university_km": req.dist_nearest_university_km,
        "dist_main_bus_route_m": req.dist_main_bus_route_m,
        "road_width_ft": req.road_width_ft,
        "pipe_water_available": req.pipe_water_available,
        "three_phase_electricity": req.three_phase_electricity,
        "facing_road_frontage_ft": req.perch_size * 2.8 + 10.0
    }

    df_single = pd.DataFrame([row_data])
    X_proc = state["preprocessor"].transform(df_single)

    # Prediction
    best_model = state["best_model"]
    pred_perch_price = float(best_model.predict(X_proc)[0])
    total_price_millions = float(round((pred_perch_price * req.perch_size) / 10.0, 2))

    # Local SHAP Explainability for this exact input
    explainer = state["shap_bundle"]["explainer"]
    expected_value = state["shap_bundle"]["expected_value"]
    human_feature_names = state["shap_bundle"]["human_feature_names"]

    shap_vals = explainer(X_proc)
    sample_shap = shap_vals.values[0]

    # Map features to contributions
    contributions = []
    for name, val in zip(human_feature_names, sample_shap):
        if abs(val) > 0.05:  # meaningful threshold
            contributions.append({
                "feature_name": name,
                "impact_lakhs": round(float(val), 2)
            })

    # Sort by absolute impact descending
    contributions = sorted(contributions, key=lambda x: abs(x["impact_lakhs"]), reverse=True)[:8]

    return {
        "price_per_perch_lakhs": round(pred_perch_price, 2),
        "total_price_millions": total_price_millions,
        "model_used": state["best_model_name"],
        "base_expected_value": round(expected_value, 2),
        "shap_attributions": contributions
    }

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "engine": "Colombo Suburban Land Valuation System", "model": state.get("best_model_name")}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.app:app", host="127.0.0.1", port=8000, reload=False)
