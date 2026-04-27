import streamlit as st
import pandas as pd

# =========================
# Page Config
# =========================
st.set_page_config(page_title="Results", layout="wide")

st.title("📊 Extraction Results")

st.markdown("---")

# =========================
# Check Session Data
# =========================
if "processed_data" not in st.session_state or st.session_state.processed_data is None:
    st.error("No processed data found. Please upload and process a document first.")
    st.page_link("pages/upload.py", label="Go to Upload")
    st.stop()

response = st.session_state.processed_data

# =========================
# Validate Response
# =========================
if not response.get("success", False):
    st.error("Processing failed.")
    
    errors = response.get("errors", [])
    for err in errors:
        st.error(err)

    st.stop()

data = response.get("data")

if not data:
    st.warning("No data returned.")
    st.stop()

# =========================
# Header Section
# =========================
st.subheader("📌 Invoice Summary")

col1, col2, col3, col4 = st.columns(4)

invoice = data.get("invoice", {})
totals = data.get("totals", {})

with col1:
    st.metric("Invoice Number", invoice.get("invoice_number") or "-")

with col2:
    st.metric("Invoice Date", invoice.get("invoice_date") or "-")

with col3:
    st.metric("Total", totals.get("total") or "-")

with col4:
    st.metric("Currency", data.get("currency") or "-")

st.markdown("---")

# =========================
# Supplier / Customer
# =========================
st.subheader("🏢 Parties")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Supplier")
    st.write(data.get("supplier") or "N/A")

with col2:
    st.markdown("### Customer")
    st.write(data.get("customer") or "N/A")

st.markdown("---")

# =========================
# Items Table
# =========================
st.subheader("🧾 Items")

items = data.get("items", [])

if items:
    df = pd.DataFrame(items)
    st.dataframe(df, use_container_width=True)
else:
    st.info("No items found.")

st.markdown("---")

# =========================
# Raw JSON (Debug / Transparency)
# =========================
with st.expander("🔍 View Raw JSON"):
    st.json(data)

# =========================
# Navigation Buttons
# =========================
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    if st.button("🔙 Back to Upload"):
        st.switch_page("pages/upload.py")

with col2:
    st.success("Ready for export (next step)")