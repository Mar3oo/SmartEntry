import streamlit as st

from api_client import APIError, SmartEntryAPI, infer_file_type
from components.preview import render_preview
from state import (
    current_profile,
    init_session_state,
    reset_for_selected_file,
    set_processed_response,
)


st.set_page_config(page_title="Upload Document", page_icon="📤", layout="wide")

init_session_state()
api = SmartEntryAPI()

st.title("Upload Document")
st.markdown("Upload a PDF or image invoice, then send it through the AI pipeline.")
st.markdown("---")

left, right = st.columns([2, 1])

with left:
    uploaded_file = st.file_uploader(
        "Choose an invoice file",
        type=["pdf", "png", "jpg", "jpeg"],
    )

with right:
    st.markdown("#### Current Mapping")
    st.write(current_profile())
    st.page_link("pages/schema_config.py", label="Change mapping profile")

if uploaded_file:
    reset_for_selected_file(uploaded_file)
else:
    st.session_state.uploaded_file = None

status_col1, status_col2, status_col3 = st.columns(3)
status_col1.metric("Backend File ID", st.session_state.uploaded_file_id or "-")
status_col2.metric("File Type", st.session_state.uploaded_file_type or "-")
status_col3.metric(
    "AI Status",
    "Processed" if st.session_state.processed_response else "Waiting",
)

st.markdown("---")

preview_col, action_col = st.columns([3, 2])

with preview_col:
    st.subheader("Preview")
    if st.session_state.uploaded_file:
        render_preview(st.session_state.uploaded_file)
    else:
        st.warning("No file selected.")

with action_col:
    st.subheader("Actions")

    if not st.session_state.uploaded_file:
        st.info("Select a file to enable upload and processing.")

    upload_disabled = st.session_state.uploaded_file is None
    process_disabled = not st.session_state.uploaded_file_id

    if st.button(
        "Upload to Backend",
        disabled=upload_disabled,
        use_container_width=True,
    ):
        with st.spinner("Uploading file to SmartEntry API..."):
            try:
                upload_response = api.upload_document(st.session_state.uploaded_file)
            except APIError as exc:
                st.error(str(exc))
                if exc.details:
                    st.caption(exc.details)
            else:
                st.session_state.upload_response = upload_response
                st.session_state.uploaded_file_id = upload_response.get("file_id")
                st.session_state.uploaded_file_path = upload_response.get("file_path")
                st.session_state.uploaded_file_name = st.session_state.uploaded_file.name
                st.session_state.uploaded_file_type = infer_file_type(
                    st.session_state.uploaded_file
                )
                st.success("Upload complete.")

    if st.session_state.uploaded_file_id:
        st.success("File is ready to process.")
        st.caption(st.session_state.uploaded_file_path)

    if st.button(
        "Process with AI",
        type="primary",
        disabled=process_disabled,
        use_container_width=True,
    ):
        with st.spinner("Processing document with AI..."):
            try:
                response = api.process_document(
                    file_id=st.session_state.uploaded_file_id,
                    file_path=st.session_state.uploaded_file_path,
                    file_type=st.session_state.uploaded_file_type,
                    profile=current_profile(),
                )
            except APIError as exc:
                st.error(str(exc))
                if exc.details:
                    st.caption(exc.details)
            else:
                set_processed_response(response)
                if response.get("success", False):
                    st.success("Processing completed.")
                else:
                    st.warning("Processing completed with errors.")
                st.switch_page("pages/results.py")

    st.page_link("pages/results.py", label="Open Results")

st.markdown("---")
st.info("Supported formats: PDF, PNG, JPG, JPEG")
