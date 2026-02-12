import streamlit as st
from core.scraper import fetch_offers
from core.rate_engine import (
    filter_electric_residential,
    compute_monthly_cost,
    score_plans
)

# -----------------------------
# Atrium Intelligence Header
# -----------------------------
st.markdown("""
# ⚡ Atrium Intelligence  
### New York Electric Rate Optimizer (Demo)
Helping customers pay less for electricity — instantly.
""")

# -----------------------------
# User Inputs
# -----------------------------
zip_code = st.text_input("Enter ZIP Code", "10001")
usage = st.number_input("Monthly Usage (kWh)", min_value=1, value=600)

st.markdown("### Preferences")
prefer_fixed = st.checkbox("Prefer fixed-rate plans")
prefer_green = st.checkbox("Prefer green energy")
avoid_cancellation_fees = st.checkbox("Avoid cancellation fees")
avoid_value_added = st.checkbox("Avoid value-added services")

# -----------------------------
# Run Optimization
# -----------------------------
if st.button("Find Best Plans"):
    try:
        df = fetch_offers(zip_code)

        if df.empty:
            st.error("No offers returned for this ZIP code.")
        else:
            df = filter_electric_residential(df)

            if df.empty:
                st.error("No electric residential offers found for this ZIP code.")
            else:

                # -----------------------------
                # Detect Utility (Reliable)
                # -----------------------------
                utility_fields = ["SERVICE_ZONE", "UTILITY", "SERVICE_TERRITORY"]

                utility_name = None
                for field in utility_fields:
                    if field in df.columns and df[field].notna().any():
                        utility_name = df[field].mode()[0]
                        break
                    
                if not utility_name:
                    utility_name = "Unknown Utility"

                st.subheader("Utility Detected")
                st.info(f"""
                **{utility_name}** serves your address.

                This matters because:
                - Only ESCOs approved in **{utility_name}** territory can offer plans to you  
                - Your **default supply rate** comes from {utility_name}  
                - Your savings are calculated against {utility_name}'s supply rate  
                - Two customers in the same ZIP may have different utilities  
                """)

                # -----------------------------
                # Allow User to Override Utility
                # -----------------------------
                st.markdown("### Override Utility (Optional)")
                user_utility = st.text_input("If this utility is incorrect, enter the correct one:", value=utility_name)
                utility_name = user_utility



                # -----------------------------
                # Default Utility Rate Card
                # -----------------------------
                default_utility_df = df[df["SERVICE_ZONE"].str.contains(utility_name, case=False, na=False)]
                if not default_utility_df.empty:
                    default_rate = default_utility_df.iloc[0]["RATE"]
                    st.subheader("Default Utility Supply Rate")
                    st.info(f"""
Your utility (**{user_utility}**) currently charges **${default_rate:.4f}/kWh**  
This is the baseline used to calculate your savings.
""")
                else:
                    default_rate = None
                    st.subheader("Default Utility Supply Rate")
                    st.warning("Default utility rate not found for this utility.")

                # -----------------------------
                # Why Utility Matters Card
                # -----------------------------
                with st.expander("Why Your Utility Matters"):
                    st.write("""
Your utility determines:
- Which ESCOs can serve you  
- Which plans you are eligible for  
- Your default supply rate  
- Your potential savings  
- Your switching process and timeline  

Even customers in the same ZIP code may have different utilities.
""")

                # -----------------------------
                # Score Plans Based on Usage + Preferences
                # -----------------------------
                df_scored = score_plans(
                    df,
                    usage,
                    prefer_fixed=prefer_fixed,
                    prefer_green=prefer_green,
                    avoid_cancellation_fees=avoid_cancellation_fees,
                    avoid_value_added=avoid_value_added
                )

                # Top 5 best-value plans
                top5 = df_scored.head(5)
                best_plan = top5.iloc[0]

                # -----------------------------
                # Savings Card
                # -----------------------------
                st.subheader("Your Savings")
                if default_rate is not None:
                    savings = (default_rate - best_plan["RATE"]) * usage
                    st.success(f"You save **${savings:.2f} per month** by switching to the best-value plan.")
                else:
                    st.info("Default utility rate not found — savings unavailable.")

                # -----------------------------
                # Best Plan Card
                # -----------------------------
                st.subheader("Best Value Plan (Based on Your Usage & Preferences)")
                st.write({
                    "Provider": best_plan["DISPLAY_NAME"],
                    "Rate ($/kWh)": best_plan["RATE"],
                    "Monthly Cost": best_plan["monthly_cost"],
                    "Offer Type": best_plan["OFFER_TYPE"],
                    "Zone": best_plan["SERVICE_ZONE"],
                    "Green %": best_plan["PERCENTAGE_GREEN"],
                    "Cancellation Fee": best_plan.get("CANCELLATION_FEE", "N/A")
                })

                # -----------------------------
                # Switch Now Button (Homepage Only)
                # -----------------------------
                st.subheader("Switch to This Plan")

                provider_url = best_plan.get("URL", None)
                provider_name = best_plan["DISPLAY_NAME"]

                if provider_url and provider_url != "0":
                    st.markdown(f"[👉 Switch Now]({provider_url})")
                else:
                    ptc_home = "https://documents.dps.ny.gov/PTC"
                    st.markdown(f"[👉 Open PowerToChoose]({ptc_home})")

                    st.info(f"""
After the page loads:

1. Scroll down and click **Accept** on the disclaimer popup.  
2. In the search bar, type: **{provider_name}**  
3. Select the provider from the list.  
4. Choose the plan that matches the name shown above.  
""")

                # -----------------------------
                # Explanation Modal
                # -----------------------------
                with st.expander("Why This Plan Is Best for You"):
                    st.write("""
This recommendation is based on:
- Your monthly usage  
- Your preferences (fixed rate, green energy, no cancellation fees, etc.)  
- Total monthly cost  
- Plan structure (fees, rate type, green %, value-added services)  
- A scoring model that balances cost, risk, and preferences  
""")

                # -----------------------------
                # Top 5 Plans Table
                # -----------------------------
                st.subheader("Top 5 Best Value Plans")
                st.dataframe(top5)

                # -----------------------------
                # Full Table
                # -----------------------------
                with st.expander("See All Plans"):
                    st.dataframe(df_scored)

    except Exception as e:
        st.error(f"An error occurred: {e}")