"""
BMI Calculator — Streamlit
---------------------------------
Professional, medical-themed BMI calculator with dual-unit inputs,
color-coded results, category mapping, and simple recommendations.
For educational purposes only; not medical advice.
"""

from __future__ import annotations
import math
import typing as t

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt


# ----------------------------- Constants -----------------------------
APP_TITLE = "BMI Calculator"
APP_SUBTITLE = "Body Mass Index — Educational Tool"

# Thresholds: (label, lower_bound_inclusive, upper_bound_exclusive, color)
BMI_BANDS: t.List[t.Tuple[str, float, float, str]] = [
    ("Underweight", 0.0, 18.5, "#1976D2"),  # blue
    ("Normal", 18.5, 25.0, "#2E7D32"),      # green
    ("Overweight", 25.0, 30.0, "#ED6C02"),  # amber
    ("Obese", 30.0, float("inf"), "#C62828")# red
]

CSS = """
<style>
:root {
  --primary: #0B6E99;
  --accent:  #2A9D8F;
  --ok:      #2E7D32;
  --warn:    #ED6C02;
  --alert:   #C62828;
  --info:    #1976D2;
  --card-bg: #F7FAFC;
  --muted:   #6B7280;
}
.title-bar {
  padding: 0.6rem 1rem;
  border-left: 6px solid var(--primary);
  background: linear-gradient(90deg, #ffffff 0%, #f1f7fb 100%);
  border-radius: 6px;
  margin-bottom: 1rem;
}
.kpi-card {
  background: var(--card-bg);
  border: 1px solid #E5E7EB;
  border-radius: 10px;
  padding: 1rem 1.25rem;
  margin-top: 0.5rem;
}
.badge {
  display: inline-block;
  padding: 0.25rem 0.6rem;
  border-radius: 999px;
  font-weight: 600;
  font-size: 0.95rem;
  color: white;
}
.badge.info { background: var(--info); }
.badge.ok   { background: var(--ok); }
.badge.warn { background: var(--warn); }
.badge.alert{ background: var(--alert); }
.disclaimer {
  font-size: 0.85rem;
  color: var(--muted);
}
.foot {
  color: var(--muted);
  font-size: 0.8rem;
  margin-top: 1.5rem;
}
</style>
"""


# ----------------------------- Core Logic -----------------------------
def kg_from_lbs(pounds: float) -> float:
    return pounds * 0.45359237


def meters_from_inches(inches: float) -> float:
    return inches * 0.0254


def bmi(weight_kg: float, height_m: float) -> float:
    """Compute BMI = kg / m^2. Returns NaN if inputs invalid."""
    if height_m <= 0 or weight_kg <= 0:
        return float("nan")
    return weight_kg / (height_m ** 2)


def classify_bmi(bmi_value: float) -> t.Tuple[str, str]:
    """Return (category, tone) for badge styling."""
    if math.isnan(bmi_value):
        return "—", "info"
    if bmi_value < 18.5:
        return "Underweight", "info"
    if bmi_value < 25.0:
        return "Normal", "ok"
    if bmi_value < 30.0:
        return "Overweight", "warn"
    return "Obese", "alert"


def recommendations(category: str) -> t.List[str]:
    recs = {
        "Underweight": [
            "Discuss weight goals with a clinician or dietitian.",
            "Increase nutrient-dense calories; emphasize lean proteins and complex carbs.",
            "Screen for underlying causes (e.g., thyroid, malabsorption).",
            "Incorporate progressive resistance training."
        ],
        "Normal": [
            "Maintain balanced diet per evidence-based guidelines.",
            "Target ≥150 minutes/week of moderate activity.",
            "Prioritize sleep hygiene and stress management.",
            "Continue routine preventive care."
        ],
        "Overweight": [
            "Adopt calorie-aware, whole-food eating patterns.",
            "Increase physical activity; combine aerobic and strength training.",
            "Set incremental goals (e.g., 5–7% weight reduction).",
            "Consider coaching or registered dietitian support."
        ],
        "Obese": [
            "Partner with a clinician for a comprehensive plan.",
            "Combine nutrition therapy, activity, and behavior strategies.",
            "Discuss adjuncts when appropriate (pharmacotherapy, bariatric referral).",
            "Address comorbidities (HTN, T2DM, OSA) and monitor regularly."
        ],
        "—": []
    }
    return recs.get(category, [])


def render_band_chart(bmi_value: float) -> alt.Chart:
    """Color-coded range bars + current BMI marker."""
    # Chart ranges
    # Cap the display domain to a sensible range for context
    display_min, display_max = 10.0, 40.0

    thresholds = pd.DataFrame({
        "range": ["Underweight", "Normal", "Overweight", "Obese"],
        "start": [10.0, 18.5, 25.0, 30.0],
        "end":   [18.5, 25.0, 30.0, 40.0],
        "color": ["#1976D2", "#2E7D32", "#ED6C02", "#C62828"]
    })

    point_val = float(np.clip(bmi_value if not math.isnan(bmi_value) else 0, display_min, display_max))
    point = pd.DataFrame({"BMI": [point_val]})

    base = (
        alt.Chart(thresholds)
        .mark_bar()
        .encode(
            x=alt.X("start:Q", scale=alt.Scale(domain=[display_min, display_max]),
                    axis=alt.Axis(title="BMI (kg/m²)")),
            x2="end:Q",
            color=alt.Color("range:N", scale=alt.Scale(range=thresholds["color"].tolist()), legend=None),
            tooltip=["range", "start", "end"]
        )
        .properties(height=44)
    )

    marker = alt.Chart(point).mark_tick(size=44, thickness=2).encode(x="BMI:Q")

    return base + marker


# ----------------------------- Streamlit App -----------------------------
def main() -> None:
    st.set_page_config(page_title="BMI Calculator | Health Education", page_icon="⚕️", layout="centered")
    st.markdown(CSS, unsafe_allow_html=True)

    # Title
    st.markdown(
        f"<div class='title-bar'><h1 style='margin:0'>{APP_TITLE}</h1>"
        f"<p style='margin:0.25rem 0 0;color:#334155'>{APP_SUBTITLE}</p></div>",
        unsafe_allow_html=True
    )

    # Sidebar — Units & Guidance
    with st.sidebar:
        st.subheader("Units")
        unit_system = st.radio(
            "Measurement system",
            ["Metric (cm, kg)", "Imperial (in, lbs)"],
            index=0,
            help="Choose input units. Calculations are performed in metric."
        )
        st.markdown("---")
        st.caption("Tip: Accurate height and weight improve BMI precision.")

    # Inputs
    col1, col2 = st.columns(2)
    if "Metric" in unit_system:
        with col1:
            height_cm = st.number_input(
                "Height (cm)", min_value=50.0, max_value=250.0, value=170.0, step=0.1
            )
        with col2:
            weight_kg = st.number_input(
                "Weight (kg)", min_value=20.0, max_value=300.0, value=70.0, step=0.1
            )
        height_m = height_cm / 100.0
        weight = weight_kg
    else:
        with col1:
            height_in = st.number_input(
                "Height (inches)", min_value=20.0, max_value=100.0, value=67.0, step=0.1
            )
        with col2:
            weight_lb = st.number_input(
                "Weight (lbs)", min_value=44.0, max_value=660.0, value=154.0, step=0.1
            )
        height_m = meters_from_inches(height_in)
        weight = kg_from_lbs(weight_lb)

    # Compute
    bmi_value = round(bmi(weight, height_m), 1) if height_m > 0 and weight > 0 else float("nan")
    category, tone = classify_bmi(bmi_value)

    # Results
    st.markdown("### Results")
    st.markdown("<div class='kpi-card'>", unsafe_allow_html=True)
    if math.isnan(bmi_value):
        st.info("Enter valid height and weight to calculate BMI.")
    else:
        st.write("**Your BMI**")
        st.markdown(f"<span class='badge {tone}'>{bmi_value}</span>", unsafe_allow_html=True)
        st.write("**Category**")
        st.markdown(f"<span class='badge {tone}'>{category}</span>", unsafe_allow_html=True)

        chart = render_band_chart(bmi_value)
        st.altair_chart(chart, use_container_width=True)

        st.write("**Recommendations**")
        for r in recommendations(category):
            st.write(f"- {r}")
    st.markdown("</div>", unsafe_allow_html=True)

    # Disclaimer
    st.markdown("---")
    st.markdown(
        "<p class='disclaimer'>Disclaimer: This tool is for educational purposes only and does not provide "
        "medical advice. Consult a qualified healthcare professional for personalized assessment, diagnosis, "
        "and treatment.</p>",
        unsafe_allow_html=True
    )

    # Footer
    st.markdown("<div class='foot'>© 2025 Health Education Demo</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
