import streamlit as st

from api_client import get_api_base_url
from state import init_session_state


st.set_page_config(
    page_title="SmartEntry",
    page_icon="📄",
    layout="wide",
)

init_session_state()

with st.sidebar:
    st.title("📄 SmartEntry")
    st.markdown("### Navigation")
    st.page_link("pages/upload.py", label="Upload Document")
    st.page_link("pages/results.py", label="View Results")
    st.page_link("pages/schema_config.py", label="Schema Config")
    st.markdown("---")
    st.markdown("### System Status")
    st.success("Frontend Ready")
    st.info(f"Backend: {get_api_base_url()}")

st.title("SmartEntry System")

st.markdown(
    """
Welcome to **SmartEntry**, an AI-powered invoice processing system.

Upload an invoice, run the AI pipeline, review the mapped rows, save corrections
back to memory, and export the result to Excel.
"""
)

st.markdown("---")
st.subheader("Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### Upload")
    st.write("Upload a document to start processing.")
    st.page_link("pages/upload.py", label="Go to Upload")

with col2:
    st.markdown("### Results")
    st.write("Review mapped rows and save corrections.")
    st.page_link("pages/results.py", label="View Results")

with col3:
    st.markdown("### Schema")
    st.write("Configure schema and mappings.")
    st.page_link("pages/schema_config.py", label="Configure")

st.markdown("---")
st.subheader("How It Works")

st.markdown(
    """
1. Upload a PDF or image invoice.
2. SmartEntry saves the file through the backend API.
3. The AI pipeline extracts, validates, and maps invoice data.
4. You edit the mapped table, save corrections, and export Excel.
"""
)

st.markdown("---")
st.caption("SmartEntry · AI Document Processing System")
