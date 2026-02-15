import streamlit as st
from core.ct_scraper import fetch_ct_offers_df

st.title("CT – Eversource Business Offers")

if st.button("Fetch live offers"):
    with st.spinner("Contacting EnergizeCT…"):
        df = fetch_ct_offers_df()
    st.write(df)