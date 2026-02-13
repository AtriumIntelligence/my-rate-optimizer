import streamlit as st
import streamlit as st
from core.ct_scraper import fetch_ct_offers_selenium

st.title("Connecticut Commercial Optimizer")

if st.button("Load Eversource CT Supplier Offers"):
    with st.spinner("Fetching offers..."):
        df = fetch_ct_offers_selenium()
    st.success(f"Loaded {len(df)} offers.")
    st.dataframe(df)