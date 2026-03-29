import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide", page_title="Digital Twin Dashboard")

@st.cache_data
def generate_mock_data():
    np.random.seed(42)
    
    # Region-specific agricultural data with accurate Tunisian crop distribution
    region_data = {
        "Sfax": {
            "crops": ["Olive", "Citrus", "Date Palm"],
            "lat_range": (34.6, 34.9),
            "lon_range": (10.4, 10.8),
            "description": "Major olive oil production region with coastal groves"
        },
        "Cap Bon": {
            "crops": ["Citrus", "Olive", "Tomato"],
            "lat_range": (36.4, 36.7),
            "lon_range": (10.1, 10.5),
            "description": "Northern citrus belt - oranges, lemons, grapefruits"
        },
        "Kairouan": {
            "crops": ["Citrus", "Olive", "Wheat"],
            "lat_range": (35.5, 35.8),
            "lon_range": (9.7, 10.1),
            "description": "Central citrus region with olive groves"
        },
        "Sidi Bouzid": {
            "crops": ["Date Palm", "Olive", "Wheat"],
            "lat_range": (34.9, 35.2),
            "lon_range": (9.1, 9.5),
            "description": "Southern oases with extensive date palm plantations"
        },
        "Gabes": {
            "crops": ["Date Palm", "Olive", "Citrus"],
            "lat_range": (33.7, 34.1),
            "lon_range": (9.7, 10.1),
            "description": "Coastal southern region famous for dates and olives"
        }
    }
    
    soil_types = ["Clay", "Sandy", "Loam", "Silt"]
    
    data = []
    for i in range(50):
        # Select region and get its data
        region = np.random.choice(list(region_data.keys()))
        region_info = region_data[region]
        
        # Generate coordinates within agricultural areas
        latitude = np.random.uniform(region_info["lat_range"][0], region_info["lat_range"][1])
        longitude = np.random.uniform(region_info["lon_range"][0], region_info["lon_range"][1])
        
        lst = np.random.uniform(25, 45)
        ta = np.random.uniform(20, 40)
        cwsi_val = max(0.0, min(1.0, (lst - ta) / 10.0 + np.random.normal(0, 0.1)))
        
        if cwsi_val < 0.3:
            label = "Healthy"
        elif cwsi_val < 0.7:
            label = "Moderate Stress"
        else:
            label = "Severe Stress"
            
        data.append({
            "id": f"FARM-{i:03d}",
            "date": "2026-03-29",
            "region": region,
            "latitude": latitude,
            "longitude": longitude,
            "soil_type": np.random.choice(soil_types),
            "crop_type": np.random.choice(region_info["crops"]),
            "month": 3,
            "year": 2026,
            "lst_celsius": lst,
            "ndvi": np.random.uniform(0.2, 0.85),
            "savi": np.random.uniform(0.15, 0.75),
            "evi": np.random.uniform(0.1, 0.7),
            "ta_celsius": ta,
            "rh_percent": np.random.uniform(20, 85),
            "wind_ms": np.random.uniform(0.5, 12.0),
            "solar_wm2": np.random.uniform(200, 900),
            "vpd_kpa": np.random.uniform(0.5, 3.5),
            "et0_mm_day": np.random.uniform(2, 9),
            "soil_moisture": np.random.uniform(10, 45),
            "field_capacity": 35.0,
            "wilting_point": 15.0,
            "irrigation_event": np.random.choice([0, 1], p=[0.8, 0.2]),
            "cwsi": 100*cwsi_val,
            "stress_label": label
        })
    return pd.DataFrame(data)

df = generate_mock_data()

st.title("Tunisia Soil & Crop Digital Twin")

col_filter, col_map = st.columns([1, 3])

with col_filter:
    st.subheader("Filters")
    selected_region = st.selectbox("Region", ["All"] + list(df['region'].unique()))
    selected_crop = st.selectbox("Crop Type", ["All"] + list(df['crop_type'].unique()))
    
    filtered_df = df.copy()
    if selected_region != "All":
        filtered_df = filtered_df[filtered_df['region'] == selected_region]
    if selected_crop != "All":
        filtered_df = filtered_df[filtered_df['crop_type'] == selected_crop]

    st.metric("Total Farms Displayed", len(filtered_df))

with col_map:
    m = folium.Map(location=[35.0, 9.5], zoom_start=7)
    
    for _, row in filtered_df.iterrows():
        color = "green" if row['stress_label'] == "Healthy" else "orange" if row['stress_label'] == "Moderate Stress" else "red"
        
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=7,
            color=color,
            fill=True,
            fill_opacity=0.7,
            popup=f"{row['id']} | {row['crop_type']} | CWSI: {row['cwsi']:.2f}%"
        ).add_to(m)
        
    st_folium(m, height=450, width=800, returned_objects=[])

st.subheader("Field Data Matrix & Targets")

if not filtered_df.empty:
    for _, row in filtered_df.iterrows():
        with st.expander(f"{row['id']} - {row['region']} ({row['crop_type']}) | Date: {row['date']}"):
            
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("LST (°C)", f"{row['lst_celsius']:.2f}")
            c2.metric("Air Temp (°C)", f"{row['ta_celsius']:.2f}")
            c3.metric("NDVI", f"{row['ndvi']:.2f}")
            c4.metric("Soil Moisture (%)", f"{row['soil_moisture']:.2f}")
            c5.metric("VPD (kPa)", f"{row['vpd_kpa']:.2f}")
            
            st.divider()
            
            t1, t2, t3 = st.columns(3)
            t1.metric("TARGET: CWSI", f"{row['cwsi']:.3f}")
            
            label_color = "normal"
            if row['stress_label'] == "Severe Stress":
                label_color = "inverse"
            
            t2.metric("TARGET: Stress Label", row['stress_label'], delta_color=label_color)
            t3.metric("Irrigation Event", "Yes" if row['irrigation_event'] == 1 else "No")
            
            st.write(row.to_dict())
else:
    st.warning("No data points match the selected filters.")