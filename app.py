import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from calculations import (
    calculate_design,
    calculate_parametric_curve,
    calculate_energy_yield_curve,
)

from constants import (
    DEFAULT_C_DTH,
    DEFAULT_CLEARANCE,
    DEFAULT_RATED_POWER_KW,
    DEFAULT_CP,
    DEFAULT_GENERATOR_EFFICIENCY,
    DEFAULT_CAPACITY_FACTOR,
    ELLIPSE_THROAT_VELOCITY_FACTOR,
)

st.set_page_config(
    page_title="LTA Elliptical Shroud Design Tool",
    page_icon="🌬️",
    layout="wide"
)

st.markdown("""
<style>
.card {
    padding: 24px;
    border-radius: 16px;
    border: 1px solid #dbe3ef;
    background-color: white;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    min-height: 130px;
}
.card-title {
    font-size: 16px;
    color: #0f1f3d;
}
.card-value {
    font-size: 30px;
    font-weight: 800;
    color: #0647a8;
}
.safe {
    color: #07943b;
    font-weight: 800;
}
.not-safe {
    color: #cc0000;
    font-weight: 800;
}
.sidebar-title {
    font-size: 19px;
    font-weight: 800;
    color: #003b8f;
    margin-top: 22px;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="sidebar-title">📋 Project Information</div>', unsafe_allow_html=True)
    project_name = st.text_input("Project Name", "LTA Wind Energy System")

    st.markdown('<div class="sidebar-title">🌍 Site Conditions</div>', unsafe_allow_html=True)
    altitude = st.number_input("Altitude (m)", value=150.0)
    wind_speed = st.number_input("Wind Speed at Altitude (m/s)", value=7.0)
    air_density = st.number_input("Air Density (kg/m³)", value=1.22)

    st.markdown('<div class="sidebar-title">⚙️ Wind Turbine</div>', unsafe_allow_html=True)
    rotor_diameter = st.number_input("WT Diameter (m)", value=4.30)
    clearance = st.number_input("Clearance per Side (m)", value=DEFAULT_CLEARANCE)
    turbine_mass = st.number_input("Turbine Mass (kg)", value=165.0)

    st.markdown('<div class="sidebar-title">⚡ Energy Yield Inputs</div>', unsafe_allow_html=True)
    rated_power_kw = st.number_input("Rated Power (kW)", value=DEFAULT_RATED_POWER_KW)
    cp = st.number_input("Power Coefficient Cp", value=DEFAULT_CP)
    generator_efficiency = st.number_input(
        "Generator Efficiency",
        value=DEFAULT_GENERATOR_EFFICIENCY
    )
    capacity_factor = st.number_input(
        "Capacity Factor",
        value=DEFAULT_CAPACITY_FACTOR
    )

    st.markdown('<div class="sidebar-title">🎈 Elliptical Shroud Material</div>', unsafe_allow_html=True)
    shell_material_density = st.number_input(
        "Shell Material Mass per Area (kg/m²)",
        value=0.203
    )
    safety_factor = st.number_input("Buoyancy Safety Factor", value=0.80)

    calculate = st.button("🧮 Calculate Elliptical Shroud", use_container_width=True)

st.title("🌬️ LTA Elliptical Shroud Design Tool")
st.write("Engineering sizing tool for an LTA wind energy system using an elliptical shroud.")

inputs = {
    "project_name": project_name,
    "altitude": altitude,
    "wind_speed": wind_speed,
    "air_density": air_density,
    "rotor_diameter": rotor_diameter,
    "clearance": clearance,
    "turbine_mass": turbine_mass,
    "shell_material_density": shell_material_density,
    "safety_factor": safety_factor,
    "rated_power_kw": rated_power_kw,
    "cp": cp,
    "generator_efficiency": generator_efficiency,
    "capacity_factor": capacity_factor,
}

if calculate:
    st.session_state["design"] = calculate_design(inputs, DEFAULT_C_DTH)
    st.session_state["curve"] = calculate_parametric_curve(inputs)
    st.session_state["energy_curve"] = calculate_energy_yield_curve(inputs)

if "design" not in st.session_state:
    st.info("Enter the design inputs from the sidebar, then click Calculate Elliptical Shroud.")
    st.stop()

row = st.session_state["design"]
curve_df = pd.DataFrame(st.session_state["curve"])
energy_curve_df = pd.DataFrame(st.session_state["energy_curve"])

safe_df = curve_df[curve_df["Uplift / Total Mass Ratio"] < 1]

if not safe_df.empty:
    recommended_safe = safe_df.iloc[
        (safe_df["Uplift / Total Mass Ratio"] - 1).abs().argsort()[:1]
    ].iloc[0]
else:
    recommended_safe = None

if recommended_safe is not None:
    optimum_cdth = recommended_safe["C/Dth"]
    optimum_ratio = recommended_safe["Uplift / Total Mass Ratio"]
    recommended_cdth_text = f"{optimum_cdth:.2f}"
    recommended_ratio_text = f"Ratio = {optimum_ratio:.3f}"
    recommended_status = "SAFE"
    recommended_status_class = "safe"
else:
    optimum_cdth = "-"
    optimum_ratio = "-"
    recommended_cdth_text = "-"
    recommended_ratio_text = "No safe ratio below unity"
    recommended_status = "NO SAFE VALUE"
    recommended_status_class = "not-safe"

st.subheader("📊 Design Summary")
st.success("Calculation completed successfully.")

c1, c2 = st.columns(2)

with c1:
    st.markdown(f"""
    <div class="card">
        <div class="card-title">📦 Shell Volume</div>
        <div class="card-value">{row["Shell Volume (m³)"]:,} m³</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="card">
        <div class="card-title">📏 System Surface Area</div>
        <div class="card-value">{row["System Surface Area (m²)"]:,} m²</div>
    </div>
    """, unsafe_allow_html=True)

c3, c4 = st.columns(2)

with c3:
    st.markdown(f"""
    <div class="card">
        <div class="card-title">⚖️ Total System Mass</div>
        <div class="card-value">{row["Total Mass (kg)"]:,} kg</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="card">
        <div class="card-title">🎈 Optimum C/Dth Ratio</div>
        <div class="card-value">{recommended_cdth_text}</div>
        <div class="{recommended_status_class}">{recommended_status}</div>
        <div>{recommended_ratio_text}</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📐 Geometry",
    "⚖️ Mass Breakdown",
    "🎈 Buoyancy Check",
    "📈 Parametric Study",
    "⚡ Energy Yield"
])

with tab1:
    st.subheader("Geometry Parameters")

    geometry_df = pd.DataFrame({
        "Parameter": [
            "WT Diameter",
            "Clearance per Side",
            "Throat Diameter",
            "Optimum C/Dth Ratio",
            "Chord Length at Optimum C/Dth",
            "Elliptical Minor Axis at Optimum C/Dth",
            "Shell Diameter at Optimum C/Dth",
            "Cross-section Area",
            "Shell Volume",
            "Ellipse h",
            "Ellipse Perimeter",
            "Shroud Surface Area",
            "Wing Surface Area",
            "System Surface Area"
        ],
        "Value": [
            row["WT Diameter (m)"],
            row.get("Clearance per Side (m)", row.get("Clearance Ratio", clearance)),            row["Throat Diameter (m)"],
            optimum_cdth,
            row["Chord Length (m)"],
            row["Elliptical Minor Axis (m)"],
            row["Shell Diameter (m)"],
            row["Cross-section Area (m²)"],
            row["Shell Volume (m³)"],
            row["Ellipse h"],
            row["Ellipse Perimeter (m)"],
            row["Shroud Surface Area (m²)"],
            row["Wing Surface Area (m²)"],
            row["System Surface Area (m²)"],
        ],
        "Unit": [
            "m", "m", "m", "-", "m", "m", "m", "m²", "m³",
            "-", "m", "m²", "m²", "m²"
        ]
    })

    st.dataframe(geometry_df, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Mass Breakdown")

    mass_df = pd.DataFrame({
        "Component": [
            "Gas Mass",
            "Wing Mass",
            "Shroud Mass",
            "Tether Mass",
            "Turbine Mass",
            "Total Mass"
        ],
        "Mass (kg)": [
            row["Gas Mass (kg)"],
            row["Wing Mass (kg)"],
            row["Shroud Mass (kg)"],
            row["Tether Mass (kg)"],
            row["Turbine Mass (kg)"],
            row["Total Mass (kg)"]
        ]
    })

    st.dataframe(mass_df, use_container_width=True, hide_index=True)

with tab3:
    st.subheader("Buoyancy Check")

    buoyancy_df = pd.DataFrame({
        "Parameter": [
            "Buoyancy Force",
            "Total Uplift",
            "Uplift After Safety Factor",
            "Total System Mass",
            "Mass Margin",
            "Uplift / Total Mass Ratio"
        ],
        "Value": [
            row["Buoyancy Force (N)"],
            row["Total Uplift (kg)"],
            row["Uplift After Safety Factor (kg)"],
            row["Total Mass (kg)"],
            row["Mass Margin (kg)"],
            row["Uplift / Total Mass Ratio"],
        ],
        "Unit": [
            "N", "kg", "kg", "kg", "kg", "-"
        ]
    })

    st.dataframe(buoyancy_df, use_container_width=True, hide_index=True)

with tab4:
    st.subheader("Uplift / Total Mass Ratio vs C/Dth")
    st.write("The optimum value is the last safe C/Dth before the ratio reaches unity.")

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=curve_df["C/Dth"],
        y=curve_df["Uplift / Total Mass Ratio"],
        mode="lines+markers",
        name="Elliptical Shroud",
        line=dict(width=3)
    ))

    fig.add_trace(go.Scatter(
        x=curve_df["C/Dth"],
        y=[1] * len(curve_df),
        mode="lines",
        name="Unity Reference Line",
        line=dict(width=2, dash="dash")
    ))

    if recommended_safe is not None:
        fig.add_trace(go.Scatter(
            x=[recommended_safe["C/Dth"]],
            y=[recommended_safe["Uplift / Total Mass Ratio"]],
            mode="markers",
            name="Optimum Safe C/Dth",
            marker=dict(size=18, symbol="star", color="green")
        ))

    fig.update_layout(
        title="Uplift / Total Mass Ratio vs C/Dth",
        xaxis_title="C/Dth Ratio",
        yaxis_title="Uplift / Total Mass Ratio",
        height=550,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.12,
            xanchor="right",
            x=1.0,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="lightgray",
            borderwidth=1,
            font=dict(size=12)
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    if recommended_safe is not None:
        st.success(
            f"Optimum safe C/Dth = {recommended_safe['C/Dth']:.2f} "
            f"with ratio = {recommended_safe['Uplift / Total Mass Ratio']:.3f}"
        )
    else:
        st.warning("No safe C/Dth value was found below unity.")

with tab5:
    st.subheader("Bare WT vs Elliptical Shrouded WT Energy Yield")

    energy_df = pd.DataFrame({
        "Parameter": [
            "Free-stream Wind Speed",
            "Elliptical Throat Velocity Factor",
            "Effective Shrouded Wind Speed",
            "Bare WT Power",
            "Elliptical Shrouded WT Power",
            "Bare WT Annual Energy Yield",
            "Elliptical Shrouded WT Annual Energy Yield",
            "Energy Gain"
        ],
        "Value": [
            row["Free-stream Wind Speed (m/s)"],
            ELLIPSE_THROAT_VELOCITY_FACTOR,
            row["Effective Shrouded Wind Speed (m/s)"],
            row["Bare WT Power (kW)"],
            row["Elliptical Shrouded WT Power (kW)"],
            row["Bare WT Annual Energy Yield (kWh/year)"],
            row["Elliptical Shrouded WT Annual Energy Yield (kWh/year)"],
            row["Energy Gain (%)"]
        ],
        "Unit": [
            "m/s",
            "-",
            "m/s",
            "kW",
            "kW",
            "kWh/year",
            "kWh/year",
            "%"
        ]
    })

    st.dataframe(energy_df, use_container_width=True, hide_index=True)

    fig_energy = go.Figure()

    fig_energy.add_trace(go.Scatter(
        x=energy_curve_df["Free-stream Wind Speed (m/s)"],
        y=energy_curve_df["Bare WT Annual Energy Yield (kWh/year)"],
        mode="lines+markers",
        name="Bare WT",
        line=dict(width=3)
    ))

    fig_energy.add_trace(go.Scatter(
        x=energy_curve_df["Free-stream Wind Speed (m/s)"],
        y=energy_curve_df["Elliptical Shrouded WT Annual Energy Yield (kWh/year)"],
        mode="lines+markers",
        name="Elliptical Shrouded WT",
        line=dict(width=3)
    ))

    fig_energy.update_layout(
        title="Annual Energy Yield vs Free-stream Wind Speed",
        xaxis_title="Free-stream Wind Speed (m/s)",
        yaxis_title="Annual Energy Yield (kWh/year)",
        height=550,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.12,
            xanchor="right",
            x=1.0,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="lightgray",
            borderwidth=1,
            font=dict(size=12)
        )
    )

    st.plotly_chart(fig_energy, use_container_width=True)

    st.info(
        "The elliptical shrouded WT uses an effective throat wind speed "
        f"equal to {ELLIPSE_THROAT_VELOCITY_FACTOR} × the free-stream wind speed."
    )