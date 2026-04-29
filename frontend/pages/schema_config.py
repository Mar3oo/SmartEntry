import streamlit as st

from state import init_session_state


st.set_page_config(page_title="Schema Config", page_icon="⚙️", layout="wide")

init_session_state()

st.title("Schema Configuration")
st.markdown("Configure how extracted data is mapped and interpreted.")
st.markdown("---")

config = st.session_state.schema_config

st.subheader("Mapping Profile")

profiles = ["generic_excel", "odoo", "sap"]
profile = st.selectbox(
    "Select mapping profile",
    profiles,
    index=profiles.index(config.get("profile", "generic_excel")),
)

config["profile"] = profile
st.info(f"Current profile: {profile}")

st.markdown("---")
st.subheader("General Settings")

col1, col2 = st.columns(2)

with col1:
    currency = st.text_input(
        "Default Currency",
        value=config.get("currency", "USD"),
    )
    config["currency"] = currency

with col2:
    date_formats = ["YYYY-MM-DD", "DD/MM/YYYY", "MM/DD/YYYY"]
    date_format = st.selectbox(
        "Date Format",
        date_formats,
        index=date_formats.index(config.get("date_format", "YYYY-MM-DD")),
    )
    config["date_format"] = date_format

st.markdown("---")
st.subheader("Advanced")

st.warning("Custom field mapping and validation rules will be added later.")

st.markdown("---")

if st.button("Save Configuration"):
    st.session_state.schema_config = config
    st.success("Configuration saved.")

with st.expander("View Current Configuration"):
    st.json(config)
