import streamlit as st

# =========================
# Page Config
# =========================
st.set_page_config(page_title="Schema Config", layout="wide")

st.title("⚙️ Schema Configuration")

st.markdown("Configure how extracted data is mapped and interpreted.")

st.markdown("---")

# =========================
# Initialize Session State
# =========================
if "schema_config" not in st.session_state:
    st.session_state.schema_config = {
        "profile": "generic_excel",
        "currency": "USD",
        "date_format": "YYYY-MM-DD"
    }

config = st.session_state.schema_config

# =========================
# Profile Selection
# =========================
st.subheader("📦 Mapping Profile")

profile = st.selectbox(
    "Select mapping profile",
    ["generic_excel", "odoo", "sap"],
    index=["generic_excel", "odoo", "sap"].index(config["profile"])
)

config["profile"] = profile

st.info(f"Current profile: {profile}")

st.markdown("---")

# =========================
# General Settings
# =========================
st.subheader("🧾 General Settings")

col1, col2 = st.columns(2)

with col1:
    currency = st.text_input(
        "Default Currency",
        value=config.get("currency", "USD")
    )
    config["currency"] = currency

with col2:
    date_format = st.selectbox(
        "Date Format",
        ["YYYY-MM-DD", "DD/MM/YYYY", "MM/DD/YYYY"],
        index=["YYYY-MM-DD", "DD/MM/YYYY", "MM/DD/YYYY"].index(config.get("date_format", "YYYY-MM-DD"))
    )
    config["date_format"] = date_format

st.markdown("---")

# =========================
# Advanced (Placeholder)
# =========================
st.subheader("🧠 Advanced (Coming Soon)")

st.warning("Custom field mapping and validation rules will be added later.")

st.markdown("---")

# =========================
# Save Configuration
# =========================
if st.button("💾 Save Configuration"):
    st.session_state.schema_config = config
    st.success("Configuration saved!")

# =========================
# Display Current Config
# =========================
with st.expander("🔍 View Current Configuration"):
    st.json(config)