from __future__ import annotations

import streamlit as st
from PIL import Image


def render_preview(uploaded_file):
    if uploaded_file is None:
        st.warning("No file to preview.")
        return

    file_type = uploaded_file.type or ""

    if file_type == "application/pdf":
        st.info("PDF selected. The backend will process the saved upload.")
        st.caption(uploaded_file.name)
    elif file_type.startswith("image"):
        try:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_container_width=True)
            uploaded_file.seek(0)
        except Exception as exc:
            st.error(f"Failed to display image: {exc}")
    else:
        st.error("Unsupported file format.")
