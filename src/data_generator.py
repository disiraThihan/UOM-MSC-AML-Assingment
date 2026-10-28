"""
Colombo Suburban Land Price Dataset Generator
Focus Corridor: Malabe - Kottawa - Kaduwela - Athurugiriya - Thalawathugoda (Western Province, Sri Lanka)
Grounded in empirical UDA guidelines, Central Bank Land Price Index (Colombo District), and bank appraisal norms.
"""

import numpy as np
import pandas as pd
import json
import os

def generate_colombo_land_dataset(n_samples=2500, random_state=42):
    np.random.seed(random_state)

    localities = [
        "Malabe", "Kottawa", "Athurugiriya", "Thalawathugoda",
        "Kaduwela", "Maharagama", "Battaramulla", "Pannipitiya", "Homagama"
    ]

    # Suburb base price ranges (in Lakhs LKR per perch: 1 Lakh = 100,000 LKR)
    locality_base = {
        "Battaramulla": 32.0,
        "Thalawathugoda": 28.5,
        "Maharagama": 24.0,
        "Malabe": 21.5,
        "Pannipitiya": 18.0,
        "Kottawa": 17.5,
        "Athurugiriya": 14.0,
        "Kaduwela": 13.0,
        "Homagama": 10.5
    }

    # Typical distance to Colombo Fort CBD (km) per locality
    locality_cbd_dist = {
        "Battaramulla": (9.0, 1.2),
        "Thalawathugoda": (12.5, 1.5),
        "Maharagama": (14.0, 1.2),
        "Malabe": (14.5, 1.8),
        "Pannipitiya": (16.0, 1.5),
        "Kottawa": (18.5, 1.8),
        "Athurugiriya": (19.0, 2.0),
        "Kaduwela": (18.0, 2.0),
        "Homagama": (22.0, 2.5)
    }

    # Proximity to nearest expressway interchange (Kottawa, Athurugiriya, Kaduwela)
    locality_expressway_dist = {
        "Kottawa": (1.8, 0.9),       # Kottawa Interchange (Makumbura)
        "Athurugiriya": (2.2, 1.1),  # Athurugiriya Interchange
        "Kaduwela": (2.0, 1.0),      # Kaduwela Interchange
        "Malabe": (3.8, 1.4),        # Mid-point between Athurugiriya and Kaduwela exits
        "Thalawathugoda": (4.5, 1.5),
        "Pannipitiya": (3.5, 1.2),
        "Maharagama": (5.5, 1.6),
        "Battaramulla": (6.5, 1.8),
        "Homagama": (4.0, 1.5)
    }

    records = []

    for i in range(n_samples):
        # Sample locality with realistic suburban weights
        loc = np.random.choice(localities, p=[0.20, 0.16, 0.14, 0.12, 0.10, 0.08, 0.08, 0.06, 0.06])
        base_price = locality_base[loc]

        # Perch size: 6 to 35 perches (suburban residential plots are typically 8-15 perches)
        perch_size = np.round(np.clip(np.random.gamma(shape=3.5, scale=3.2), 6.0, 45.0), 1)

        # Distance to Colombo CBD (km)
        cbd_mean, cbd_std = locality_cbd_dist[loc]
        dist_colombo_cbd_km = np.round(np.clip(np.random.normal(cbd_mean, cbd_std), 6.0, 30.0), 2)

        # Distance to nearest expressway interchange (km)
        exp_mean, exp_std = locality_expressway_dist[loc]
        dist_expressway_km = np.round(np.clip(np.random.normal(exp_mean, exp_std), 0.4, 12.0), 2)

        # Distance to key university / IT hub (SLIIT, Horizon, CINEC, NSBM, MillenniumIT)
        # Closer in Malabe and Homagama
        if loc == "Malabe":
            dist_university_km = np.round(np.clip(np.random.exponential(scale=1.8) + 0.3, 0.3, 7.0), 2)
        elif loc == "Homagama":
            dist_university_km = np.round(np.clip(np.random.exponential(scale=2.5) + 0.5, 0.5, 9.0), 2)
        elif loc in ["Athurugiriya", "Thalawathugoda", "Kaduwela"]:
            dist_university_km = np.round(np.clip(np.random.normal(4.5, 1.5), 1.0, 10.0), 2)
        else:
            dist_university_km = np.round(np.clip(np.random.normal(7.5, 2.0), 2.0, 15.0), 2)

        # Walking distance to main bus route / corridor (meters)
        # e.g., Route 177, 174, 993, 138
        dist_main_bus_route_m = int(np.clip(np.random.exponential(scale=350) + 50, 20, 2500))

        # Access road width (feet) - critical Sri Lankan planning regulation:
        # <12ft: non-subdividable; 12-15ft: standard residential; 20ft+: UDA approved commercial/development width
        road_width_ft = np.random.choice([10, 12, 15, 20, 30, 40], p=[0.10, 0.30, 0.28, 0.22, 0.08, 0.02])

        # Road surface
        if road_width_ft >= 20:
            road_type = np.random.choice(["Carpeted", "Tarred", "Concrete"], p=[0.70, 0.25, 0.05])
        elif road_width_ft >= 12:
            road_type = np.random.choice(["Carpeted", "Tarred", "Concrete", "Gravel"], p=[0.35, 0.40, 0.15, 0.10])
        else:
            road_type = np.random.choice(["Tarred", "Concrete", "Gravel"], p=[0.30, 0.30, 0.40])

        # Zoning category
        if road_width_ft >= 20 and dist_main_bus_route_m <= 300:
            zoning = np.random.choice(["Commercial_Mixed", "Residential_High", "Residential_Medium"], p=[0.55, 0.35, 0.10])
        else:
            zoning = np.random.choice(["Residential_High", "Residential_Medium", "Agricultural_Green"], p=[0.35, 0.55, 0.10])

        # Legal deed status (Bim Saviya vs Sinnakkara)
        deed_type = np.random.choice(
            ["Bim_Saviya_First_Class", "Clear_Sinnakkara_Title", "Bim_Saviya_Second_Class", "Local_Authority_Permit"],
            p=[0.45, 0.42, 0.09, 0.04]
        )

        # Utilities
        pipe_water = 1 if np.random.rand() < (0.92 if loc in ["Battaramulla", "Thalawathugoda", "Malabe"] else 0.82) else 0
        three_phase_elec = 1 if (road_width_ft >= 15 and np.random.rand() < 0.75) else (1 if np.random.rand() < 0.40 else 0)

        # Topography & terrain
        topography = np.random.choice(
            ["Flat_Elevated", "Gentle_Slope", "Low_Lying_Filled", "Paddy_Adjacent"],
            p=[0.58, 0.22, 0.12, 0.08]
        )

        # Flood risk (specifically higher near Kelani river basin in Kaduwela or canal lowlands)
        if loc == "Kaduwela" or topography in ["Low_Lying_Filled", "Paddy_Adjacent"]:
            flood_risk = np.random.choice(["None", "Low", "Moderate", "High"], p=[0.25, 0.35, 0.25, 0.15])
        else:
            flood_risk = np.random.choice(["None", "Low", "Moderate"], p=[0.75, 0.20, 0.05])

        # Road frontage (feet)
        frontage_ft = np.round(np.clip(np.random.normal(perch_size * 2.8 + 10, 8.0), 18.0, 120.0), 1)

        # Shape regularity
        shape = np.random.choice(["Rectangular", "Square", "Irregular", "Narrow_L_Shape"], p=[0.60, 0.25, 0.11, 0.04])

        # --- NON-LINEAR VALUATION MODEL BASED ON SRI LANKAN APPRAISAL MECHANICS ---
        price = base_price

        # 1. Expressway Accessibility Multiplier (Exponential Decay)
        # Being within 2 km of Kottawa/Athurugiriya/Kaduwela interchange gives up to +25% premium
        expressway_effect = 4.5 * np.exp(-0.35 * dist_expressway_km)
        price += expressway_effect

        # 2. University / IT Park corridor proximity effect (especially in Malabe)
        if loc in ["Malabe", "Homagama"]:
            uni_effect = 3.5 * np.exp(-0.40 * dist_university_km)
            price += uni_effect
        else:
            uni_effect = 1.0 * np.exp(-0.30 * dist_university_km)
            price += uni_effect

        # 3. Main road accessibility decay
        bus_decay = -1.8 * (dist_main_bus_route_m / 1000.0)
        price += bus_decay

        # 4. Road width step-function (UDA regulations)
        if road_width_ft >= 30:
            price *= 1.25
        elif road_width_ft >= 20:
            price *= 1.15
        elif road_width_ft >= 15:
            price *= 1.04
        elif road_width_ft == 12:
            price *= 0.98
        else:  # 10ft bottleneck
            price *= 0.82

        # 5. Zoning multipliers
        if zoning == "Commercial_Mixed":
            price *= 1.30
        elif zoning == "Residential_High":
            price *= 1.08
        elif zoning == "Agricultural_Green":
            price *= 0.68

        # 6. Deed security
        if deed_type == "Bim_Saviya_First_Class":
            price *= 1.06
        elif deed_type == "Clear_Sinnakkara_Title":
            price *= 1.02
        elif deed_type == "Bim_Saviya_Second_Class":
            price *= 0.92
        else:  # Permit
            price *= 0.75

        # 7. Utilities & Infrastructure
        if pipe_water == 1:
            price += 0.8
        else:
            price -= 1.2

        if three_phase_elec == 1:
            price += 1.0

        # 8. Topography and flood risk penalties
        if topography == "Flat_Elevated":
            price *= 1.05
        elif topography == "Low_Lying_Filled":
            price *= 0.88
        elif topography == "Paddy_Adjacent":
            price *= 0.82

        if flood_risk == "High":
            price *= 0.72
        elif flood_risk == "Moderate":
            price *= 0.86
        elif flood_risk == "Low":
            price *= 0.96

        # 9. Plot shape
        if shape in ["Irregular", "Narrow_L_Shape"]:
            price *= 0.90

        # 10. Perch size marginal diminishing returns (bulk plot discount)
        if perch_size > 20:
            price *= (1.0 - 0.005 * (perch_size - 20))

        # Add realistic market negotiation noise (heteroskedastic)
        market_noise = np.random.normal(0, 0.04 * price)
        final_perch_price = np.round(np.clip(price + market_noise, 5.0, 60.0), 2)
        total_price_millions = np.round((final_perch_price * perch_size) / 10.0, 2)

        records.append({
            "property_id": f"WP-COL-{1001 + i}",
            "locality": loc,
            "perch_size": perch_size,
            "dist_expressway_interchange_km": dist_expressway_km,
            "dist_colombo_cbd_km": dist_colombo_cbd_km,
            "dist_nearest_university_km": dist_university_km,
            "dist_main_bus_route_m": dist_main_bus_route_m,
            "road_width_ft": road_width_ft,
            "road_type": road_type,
            "zoning_type": zoning,
            "deed_type": deed_type,
            "pipe_water_available": pipe_water,
            "three_phase_electricity": three_phase_elec,
            "topography": topography,
            "flood_risk_level": flood_risk,
            "facing_road_frontage_ft": frontage_ft,
            "shape_regularity": shape,
            "price_per_perch_lkr_lakhs": final_perch_price,
            "total_price_lkr_millions": total_price_millions
        })

    df = pd.DataFrame(records)
    return df

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(base_dir, "data")
    os.makedirs(out_dir, exist_ok=True)
    df = generate_colombo_land_dataset(n_samples=2500, random_state=42)
    csv_path = os.path.join(out_dir, "colombo_land_dataset.csv")
    df.to_csv(csv_path, index=False)
    print(f"Generated {len(df)} records saved to {csv_path}")
    print("\nSample Data Summary:")
    print(df.describe())
    print("\nLocality Mean Perch Prices (LKR Lakhs):")
    print(df.groupby("locality")["price_per_perch_lkr_lakhs"].mean().sort_values(ascending=False))
