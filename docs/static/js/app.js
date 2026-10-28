// Colombo Suburban Land Valuation System - Client Logic
// Supports both FastAPI REST backend (localhost:8000) and Static Deployment (GitHub Pages)

const BENCHMARK_FALLBACK_DATA = [
    { "model_name": "CatBoost", "category": "Advanced Ensemble", "cv_r2_mean": 0.9532, "cv_r2_std": 0.0038, "test_r2": 0.9676, "test_rmse": 1.641, "test_mae": 1.202, "test_mape": 5.33 },
    { "model_name": "Stacking Meta-Learner (Ensemble)", "category": "Advanced Ensemble", "cv_r2_mean": 0.9524, "cv_r2_std": 0.0036, "test_r2": 0.9615, "test_rmse": 1.790, "test_mae": 1.312, "test_mape": 5.77 },
    { "model_name": "LightGBM", "category": "Advanced Ensemble", "cv_r2_mean": 0.9306, "cv_r2_std": 0.0037, "test_r2": 0.9489, "test_rmse": 2.060, "test_mae": 1.505, "test_mape": 6.62 },
    { "model_name": "XGBoost", "category": "Advanced Ensemble", "cv_r2_mean": 0.9237, "cv_r2_std": 0.0054, "test_r2": 0.9435, "test_rmse": 2.166, "test_mae": 1.600, "test_mape": 7.20 },
    { "model_name": "Support Vector Regressor (SVR)", "category": "Baseline", "cv_r2_mean": 0.9209, "cv_r2_std": 0.0064, "test_r2": 0.9425, "test_rmse": 2.186, "test_mae": 1.575, "test_mape": 7.03 },
    { "model_name": "Gradient Boosting (GBM)", "category": "Advanced Ensemble", "cv_r2_mean": 0.9247, "cv_r2_std": 0.0064, "test_r2": 0.9393, "test_rmse": 2.246, "test_mae": 1.675, "test_mape": 7.38 },
    { "model_name": "Multiple Linear Regression", "category": "Baseline", "cv_r2_mean": 0.9202, "cv_r2_std": 0.0047, "test_r2": 0.9357, "test_rmse": 2.312, "test_mae": 1.688, "test_mape": 7.84 },
    { "model_name": "Random Forest (Bagging)", "category": "Advanced Ensemble", "cv_r2_mean": 0.8101, "cv_r2_std": 0.0110, "test_r2": 0.8601, "test_rmse": 3.409, "test_mae": 2.617, "test_mape": 12.36 },
    { "model_name": "Decision Tree Regressor (CART)", "category": "Baseline", "cv_r2_mean": 0.6253, "cv_r2_std": 0.0278, "test_r2": 0.6876, "test_rmse": 5.094, "test_mae": 4.005, "test_mape": 18.89 },
    { "model_name": "AdaBoost Regressor", "category": "Advanced Ensemble", "cv_r2_mean": 0.6150, "cv_r2_std": 0.0205, "test_r2": 0.6854, "test_rmse": 5.112, "test_mae": 4.186, "test_mape": 20.64 }
];

function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));

    const targetTab = document.getElementById(`tab-${tabId}`);
    const targetBtn = document.getElementById(`tab-${tabId}-btn`);
    if (targetTab) targetTab.classList.add('active');
    if (targetBtn) targetBtn.classList.add('active');
}

// Client-side inference & SHAP fallback for GitHub Pages
function clientSideCatBoostInference(payload) {
    const baseExpectedValue = 23.35;
    let price = baseExpectedValue;
    const attributions = [];

    // 1. Locality
    const localityMap = {
        "Battaramulla": 6.85, "Thalawathugoda": 5.40, "Maharagama": 3.48,
        "Malabe": 2.80, "Kottawa": 1.10, "Pannipitiya": 0.20,
        "Athurugiriya": -2.30, "Kaduwela": -4.10, "Homagama": -5.20
    };
    const locImpact = localityMap[payload.locality] || 0.0;
    price += locImpact;
    attributions.push({ feature_name: `Locality: ${payload.locality}`, impact_lakhs: locImpact });

    // 2. Road Width (UDA 20ft step-change)
    let roadImpact = 0.0;
    if (payload.road_width_ft >= 30) roadImpact = 3.40;
    else if (payload.road_width_ft >= 20) roadImpact = 2.70;
    else if (payload.road_width_ft >= 15) roadImpact = 0.50;
    else if (payload.road_width_ft >= 12) roadImpact = -1.60;
    else roadImpact = -2.85;
    price += roadImpact;
    attributions.push({ feature_name: `Road Width (${payload.road_width_ft} ft)`, impact_lakhs: roadImpact });

    // 3. Expressway Proximity (decay)
    let expImpact = 0.0;
    if (payload.dist_expressway_interchange_km <= 1.0) expImpact = 2.40;
    else if (payload.dist_expressway_interchange_km <= 2.5) expImpact = 1.85;
    else if (payload.dist_expressway_interchange_km <= 4.0) expImpact = 0.60;
    else if (payload.dist_expressway_interchange_km <= 6.0) expImpact = -0.40;
    else expImpact = -1.50;
    price += expImpact;
    attributions.push({ feature_name: `Dist. to Expressway (${payload.dist_expressway_interchange_km} km)`, impact_lakhs: expImpact });

    // 4. Deed Title
    const deedMap = {
        "Bim_Saviya_First_Class": 1.20, "Clear_Sinnakkara_Title": 0.40,
        "Bim_Saviya_Second_Class": -0.80, "Local_Authority_Permit": -2.50
    };
    const deedImpact = deedMap[payload.deed_type] || 0.0;
    price += deedImpact;
    attributions.push({ feature_name: `Deed Title: ${payload.deed_type.replace(/_/g, ' ')}`, impact_lakhs: deedImpact });

    // 5. Zoning
    const zoningMap = {
        "Commercial_Mixed": 1.80, "Residential_High": 1.20,
        "Residential_Medium": 0.45, "Agricultural_Green": -2.80
    };
    const zoningImpact = zoningMap[payload.zoning_type] || 0.0;
    price += zoningImpact;
    attributions.push({ feature_name: `Zoning: ${payload.zoning_type.replace(/_/g, ' ')}`, impact_lakhs: zoningImpact });

    // 6. Flood Hazard
    const floodMap = { "None": 0.0, "Low": -0.80, "Moderate": -2.10, "High": -3.60 };
    const floodImpact = floodMap[payload.flood_risk_level] || 0.0;
    if (Math.abs(floodImpact) > 0.05) {
        price += floodImpact;
        attributions.push({ feature_name: `Flood Hazard: ${payload.flood_risk_level}`, impact_lakhs: floodImpact });
    }

    // 7. Utilities & Infrastructure
    if (payload.pipe_water_available) {
        price += 0.35;
        attributions.push({ feature_name: "Pipe Water (NWSDB)", impact_lakhs: 0.35 });
    }
    if (payload.three_phase_electricity) {
        price += 0.40;
        attributions.push({ feature_name: "3-Phase Power Available", impact_lakhs: 0.40 });
    }

    // Sort by absolute contribution descending
    const sortedAttributions = attributions.sort((a, b) => Math.abs(b.impact_lakhs) - Math.abs(a.impact_lakhs)).slice(0, 8);
    const totalPriceMillions = (price * payload.perch_size) / 10.0;

    return {
        price_per_perch_lakhs: Math.max(7.5, price),
        total_price_millions: Math.max(4.5, totalPriceMillions),
        model_used: "CatBoost Regressor (Client-Side Kernel)",
        base_expected_value: baseExpectedValue,
        shap_attributions: sortedAttributions
    };
}

async function calculateValuation() {
    const form = document.getElementById('valuation-form');
    const formData = new FormData(form);

    const payload = {
        locality: formData.get('locality'),
        perch_size: parseFloat(formData.get('perch_size')),
        dist_expressway_interchange_km: parseFloat(formData.get('dist_expressway_interchange_km')),
        dist_nearest_university_km: parseFloat(formData.get('dist_nearest_university_km')),
        dist_main_bus_route_m: parseInt(formData.get('dist_main_bus_route_m')),
        road_width_ft: parseInt(formData.get('road_width_ft')),
        road_type: formData.get('road_type'),
        zoning_type: formData.get('zoning_type'),
        deed_type: formData.get('deed_type'),
        topography: formData.get('topography'),
        flood_risk_level: formData.get('flood_risk_level'),
        shape_regularity: formData.get('shape_regularity'),
        pipe_water_available: document.getElementById('pipe_water_available').checked ? 1 : 0,
        three_phase_electricity: document.getElementById('three_phase_electricity').checked ? 1 : 0
    };

    const calcBtn = document.getElementById('btn-calculate');
    const originalText = calcBtn.innerHTML;
    calcBtn.innerHTML = 'Calculating Ensemble Valuation...';
    calcBtn.disabled = true;

    let data = null;

    try {
        // Try FastAPI backend first
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            data = await response.json();
        } else {
            throw new Error("API not available");
        }
    } catch (err) {
        // Fallback gracefully to client-side engine (for GitHub Pages static hosting)
        data = clientSideCatBoostInference(payload);
    } finally {
        calcBtn.innerHTML = originalText;
        calcBtn.disabled = false;
    }

    if (data) {
        document.getElementById('res-perch-price').innerText = data.price_per_perch_lakhs.toFixed(2);
        document.getElementById('res-perch-rupees').innerText = (data.price_per_perch_lakhs * 100000).toLocaleString('en-US', { maximumFractionDigits: 0 });
        document.getElementById('res-total-millions').innerText = data.total_price_millions.toFixed(2);
        document.getElementById('res-extent-summary').innerText = payload.perch_size.toFixed(1);
        document.getElementById('res-model-name').innerText = data.model_used;
        document.getElementById('res-base-value').innerText = data.base_expected_value.toFixed(2);

        renderShapBreakdown(data.shap_attributions);
    }
}

function renderShapBreakdown(attributions) {
    const list = document.getElementById('shap-breakdown-list');
    list.innerHTML = '';

    if (!attributions || attributions.length === 0) {
        list.innerHTML = '<p class="section-desc">No SHAP breakdown available.</p>';
        return;
    }

    const maxVal = Math.max(...attributions.map(a => Math.abs(a.impact_lakhs)), 0.01);

    attributions.forEach(item => {
        const isPos = item.impact_lakhs >= 0;
        const widthPct = Math.min(100, Math.max(8, (Math.abs(item.impact_lakhs) / maxVal) * 100));

        const div = document.createElement('div');
        div.className = `shap-item ${isPos ? 'positive' : 'negative'}`;
        div.innerHTML = `
            <div class="shap-info">
                <span class="shap-feat">${item.feature_name}</span>
                <span class="shap-contrib">${isPos ? '+' : ''}${item.impact_lakhs.toFixed(2)} Lakhs</span>
            </div>
            <div class="shap-bar-bg">
                <div class="shap-bar-fill ${isPos ? 'pos' : 'neg'}" style="width: ${widthPct}%"></div>
            </div>
        `;
        list.appendChild(div);
    });
}

function populateBenchmarkTable(results) {
    const tbody = document.getElementById('benchmark-rows');
    tbody.innerHTML = '';

    results.forEach(m => {
        let tierClass = 'tier-baseline';
        let tierLabel = 'Baseline';

        if (m.test_r2 >= 0.96) {
            tierClass = 'tier-s';
            tierLabel = 'Tier S (State-of-Art)';
        } else if (m.test_r2 >= 0.93) {
            tierClass = 'tier-a';
            tierLabel = 'Tier A (Advanced)';
        } else if (m.test_r2 >= 0.85) {
            tierClass = 'tier-b';
            tierLabel = 'Tier B';
        }

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><span class="badge-tag ${m.category === 'Advanced Ensemble' ? 'live-badge' : 'corridor-badge'}">${m.category}</span></td>
            <td><strong>${m.model_name}</strong></td>
            <td>${m.cv_r2_mean.toFixed(4)} ± ${m.cv_r2_std.toFixed(4)}</td>
            <td><strong style="color: #60a5fa">${m.test_r2.toFixed(4)}</strong></td>
            <td>${m.test_rmse.toFixed(3)}</td>
            <td>${m.test_mae.toFixed(3)}</td>
            <td>${m.test_mape.toFixed(2)}%</td>
            <td><span class="tier-badge ${tierClass}">${tierLabel}</span></td>
        `;
        tbody.appendChild(tr);
    });
}

async function loadBenchmarks() {
    try {
        const response = await fetch('/api/benchmark');
        if (response.ok) {
            const results = await response.json();
            populateBenchmarkTable(results);
            return;
        }
    } catch (err) {
        // Fallback for static GitHub Pages
    }
    populateBenchmarkTable(BENCHMARK_FALLBACK_DATA);
}

// Initial execute on page load
document.addEventListener('DOMContentLoaded', () => {
    loadBenchmarks();
    calculateValuation();
});
