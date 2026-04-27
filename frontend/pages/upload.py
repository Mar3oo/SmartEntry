import streamlit as st
import time
from PIL import Image
import io

# =========================
# Page Config
# =========================
st.set_page_config(page_title="Upload Document", layout="wide")

st.title("📤 Upload Document")

st.markdown("Upload a PDF or image to extract structured data.")

st.markdown("---")

# =========================
# Initialize Session State
# =========================
if "processed_data" not in st.session_state:
    st.session_state.processed_data = None

if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None

# =========================
# File Upload Section
# =========================
uploaded_file = st.file_uploader(
    "Choose a file",
    type=["pdf", "png", "jpg", "jpeg"]
)

# Save in session state
if uploaded_file:
    st.session_state.uploaded_file = uploaded_file

st.markdown("---")

# =========================
# Preview Section
# =========================
st.subheader("📄 Preview")

if st.session_state.uploaded_file:

    file = st.session_state.uploaded_file

    if file.type == "application/pdf":
        st.info("PDF preview not rendered (can be added later)")
    else:
        image = Image.open(file)
        st.image(image, caption="Uploaded Image", use_container_width=True)

else:
    st.warning("No file uploaded")

st.markdown("---")

# =========================
# Process Section
# =========================
st.subheader("⚙️ Process Document")

process_button = st.button("🚀 Process")

if process_button:

    if not st.session_state.uploaded_file:
        st.error("Please upload a file first.")
    else:
        with st.spinner("Processing document..."):

            # Simulate processing delay
            time.sleep(2)

            # =========================
            # MOCK RESPONSE (matches backend contract)
            # =========================
            mock_response = {
                "success": True,
                "data": {
                    "supplier": None,
                    "customer": None,
                    "invoice": {
                        "invoice_number": "INV-123",
                        "invoice_date": "2024-01-01"
                    },
                    "items": [
                        {
                            "description": "Sample Item",
                            "quantity": 2,
                            "unit_price": 50,
                            "total_price": 100
                        }
                    ],
                    "totals": {
                        "total": 100
                    },
                    "currency": "USD",
                    "extra_fields": {}
                },
                "errors": [],
                "meta": None
            }

            # Save result
            st.session_state.processed_data = mock_response

        st.success("Processing completed!")

        # Navigate to results page
        st.switch_page("pages/results.py")

st.markdown("---")

# =========================
# Info Section
# =========================
st.info("Supported formats: PDF, PNG, JPG, JPEG")