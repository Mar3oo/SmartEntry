import streamlit as st
from PIL import Image


def render_preview(uploaded_file):
    """
    Render preview for uploaded file.
    Supports images and PDF (placeholder for now).
    """

    if uploaded_file is None:
        st.warning("No file to preview.")
        return

    file_type = uploaded_file.type


    if file_type == "application/pdf":
        st.info("PDF preview not supported yet.")
        st.caption("PDF rendering will be added later.")

    elif file_type.startswith("image"):
        try:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_container_width=True)
        except Exception as e:
            st.error(f"Failed to display image: {str(e)}")

    else:
        st.error("Unsupported file format.")