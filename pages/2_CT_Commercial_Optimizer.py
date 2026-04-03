import math
import pandas as pd
import streamlit as st

from core.ct_scraper import fetch_ct_offers_df


st.set_page_config(
    page_title="CT Commercial Optimizer",
    layout="wide",
)

st.title("CT Commercial Optimizer – Internal Advisor Console")

st.markdown(
    """
This internal tool compares current CT commercial supply offers (from EnergizeCT's **Print All** PDF)
against a client's existing contract, using simple, transparent assumptions.
"""
)

# -----------------------------
# Global assumptions
# -----------------------------
st.sidebar.header("Global Assumptions")

global_fixed_fee = st.sidebar.number_input(
    "Supplier Fixed Fee (per month, $)",
    min_value=0.0,
    value=0.0,
    step=5.0,
)

analysis_horizon_months = st.sidebar.number_input(
    "Analysis Horizon (months)",
    min_value=1,
    max_value=60,
    value=12,
    step=1,
)

# -----------------------------
# Client inputs
# -----------------------------
st.header("Client Usage & Current Contract")

col1, col2, col3 = st.columns(3)

with col1:
    monthly_usage_kwh = st.number_input(
        "Average Monthly Usage (kWh)",
        min_value=1,
        value=2000,
        step=100,
    )

with col2:
    current_rate_cents = st.number_input(
        "Current Supply Rate (¢/kWh)",
        min_value=0.0,
        value=13.0,
        step=0.1,
    )

with col3:
    current_fixed_fee = st.number_input(
        "Current Supplier Fixed Fee (per month, $)",
        min_value=0.0,
        value=0.0,
        step=5.0,
    )

st.markdown("---")

# -----------------------------
# Fetch CT offers from PDF
# -----------------------------
st.subheader("Current CT Supplier Offers (from EnergizeCT PDF)")

try:
    offers_df = fetch_ct_offers_df(
    customer_class=1206,
    monthly_usage=monthly_usage_kwh,
    plan_type_edc=1191,
    )
except Exception as e:
    st.error(f"Error fetching CT offers from PDF: {e}")
    st.stop()

with st.expander("Show raw parsed offers (debug)"):
    st.dataframe(offers_df)

# -----------------------------
# Cost modeling helpers
# -----------------------------
def annualized_cost(rate_cents, monthly_kwh, fixed_fee, months):
    if rate_cents is None or math.isnan(rate_cents):
        return math.nan
    variable = (rate_cents / 100.0) * monthly_kwh
    return (variable + fixed_fee) * months


# -----------------------------
# Baseline: current contract cost
# -----------------------------
current_total_cost = annualized_cost(
    current_rate_cents,
    monthly_usage_kwh,
    current_fixed_fee,
    analysis_horizon_months,
)

st.markdown(
    f"**Current contract modeled total cost over {analysis_horizon_months} months:** "
    f"${current_total_cost:,.2f}"
)

# -----------------------------
# Build comparison table
# -----------------------------
st.subheader("Modeled Offer Comparison vs Current Contract")

results = []

for _, row in offers_df.iterrows():
    rate = row["rate_cents_per_kwh"]
    supplier = row["supplier"]
    term = row["term_description"]
    recs = row["recs_pct"]

    offer_cost = annualized_cost(
        rate,
        monthly_usage_kwh,
        global_fixed_fee,
        analysis_horizon_months,
    )

    if math.isnan(offer_cost):
        continue

    savings = current_total_cost - offer_cost

    results.append(
        {
            "supplier": supplier,
            "rate_cents_per_kwh": rate,
            "term_description": term,
            "recs_pct": recs,
            "modeled_total_cost": offer_cost,
            "savings_vs_current": savings,
        }
    )

results_df = pd.DataFrame(results).sort_values(
    "savings_vs_current", ascending=False
)

st.dataframe(
    results_df.style.format(
        {
            "rate_cents_per_kwh": "{:.2f}",
            "recs_pct": "{:.1f}",
            "modeled_total_cost": "${:,.2f}",
            "savings_vs_current": "${:,.2f}",
        }
    ),
    use_container_width=True,
)

# -----------------------------
# Top recommendation
# -----------------------------
best = results_df.iloc[0]

st.markdown("### Top Modeled Recommendation")

st.markdown(
    f"""
**Supplier:** {best['supplier']}  
**Rate:** {best['rate_cents_per_kwh']:.2f} ¢/kWh  
**Term:** {best['term_description']}  
**RECs:** {best['recs_pct']} %  

**Modeled total cost over {analysis_horizon_months} months:** ${best['modeled_total_cost']:,.2f}  
**Modeled savings vs current:** ${best['savings_vs_current']:,.2f}
"""
)