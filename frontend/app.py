import streamlit as st

# =========================
# Page Configuration
# =========================
st.set_page_config(
    page_title="SmartEntry",
    page_icon="📄",
    layout="wide",
)

# =========================
# Sidebar Navigation
# =========================
with st.sidebar:
    st.title("📄 SmartEntry")

    st.markdown("### Navigation")

    st.page_link("pages/upload.py", label="📤 Upload Document")
    st.page_link("pages/results.py", label="📊 View Results")
    st.page_link("pages/schema_config.py", label="⚙️ Schema Config")

    st.markdown("---")

    st.markdown("### System Status")
    st.success("Frontend Ready")
    st.info("Backend: Not connected")

# =========================
# Main Layout
# =========================
st.title("SmartEntry System")

st.markdown(
    """
Welcome to **SmartEntry** — an AI-powered document processing system.

This application allows you to:

- Upload invoices or documents (PDF / Image)
- Extract structured data automatically
- Review and edit extracted results
- Export data to CSV / Excel
"""
)

st.markdown("---")

# =========================
# Quick Actions Section
# =========================
st.subheader("🚀 Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📤 Upload")
    st.write("Upload a document to start processing.")
    st.page_link("pages/upload.py", label="Go to Upload")

with col2:
    st.markdown("### 📊 Results")
    st.write("View extracted structured data.")
    st.page_link("pages/results.py", label="View Results")

with col3:
    st.markdown("### ⚙️ Schema")
    st.write("Configure schema and mappings.")
    st.page_link("pages/schema_config.py", label="Configure")

st.markdown("---")

# =========================
# Info Section
# =========================
st.subheader("ℹ️ How it works")

st.markdown(
    """
1. Upload your document  
2. System extracts text (PDF / OCR)  
3. AI structures the data  
4. You review and export results  
"""
)

# =========================
# Footer
# =========================
st.markdown("---")
st.caption("SmartEntry · AI Document Processing System")