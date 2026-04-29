import streamlit as st

from api_client import APIError, EXCEL_MIME_TYPE, SmartEntryAPI
from components.results_table import render_editable_results_table
from state import (
    current_profile,
    init_session_state,
    mark_saved,
    set_processed_response,
)


st.set_page_config(page_title="Results", page_icon="📊", layout="wide")

init_session_state()
api = SmartEntryAPI()

st.title("Extraction Results")
st.markdown("---")

if not st.session_state.uploaded_file_id:
    st.error("No uploaded file found. Upload a document first.")
    st.page_link("pages/upload.py", label="Go to Upload")
    st.stop()

if st.session_state.processed_response is None:
    st.warning("This file has not been processed yet.")

    if st.button("Process with AI", type="primary"):
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
                st.stop()
            else:
                set_processed_response(response)
                st.rerun()

    st.page_link("pages/upload.py", label="Back to Upload")
    st.stop()

response = st.session_state.processed_response
errors = response.get("errors", []) or []
meta = response.get("meta") or {}
rows = st.session_state.edited_rows or st.session_state.original_rows

st.subheader("Pipeline Summary")

col1, col2, col3, col4 = st.columns(4)
col1.metric("File ID", st.session_state.uploaded_file_id[:8])
col2.metric("Mapped Rows", len(rows))
col3.metric("Profile Used", meta.get("profile_used") or current_profile())
col4.metric("AI Status", "Needs review" if errors else "Ready for review")

if st.session_state.last_saved_at:
    st.success(f"Changes saved at {st.session_state.last_saved_at}.")
elif st.session_state.save_feedback:
    st.success(st.session_state.save_feedback)

if errors:
    with st.expander("Processing errors", expanded=True):
        for error in errors:
            st.error(error)

if not response.get("success", False):
    st.warning(
        "The backend reported an unsuccessful process run. Review errors before saving corrections."
    )

st.markdown("---")
st.subheader("Editable Mapped Data")

editor_key = (
    f"results_editor_{st.session_state.uploaded_file_id}_"
    f"{st.session_state.results_editor_version}"
)
edited_rows, changes = render_editable_results_table(
    original_rows=st.session_state.original_rows,
    edited_rows=rows,
    key=editor_key,
)
st.session_state.edited_rows = edited_rows

st.markdown("---")
st.subheader("Actions")

action_col1, action_col2, action_col3 = st.columns([1, 1, 1])

with action_col1:
    if st.button("Back to Upload", use_container_width=True):
        st.switch_page("pages/upload.py")

with action_col2:
    if st.button(
        "💾 Save Corrections",
        disabled=not edited_rows,
        type="primary" if changes else "secondary",
        use_container_width=True,
    ):
        with st.spinner("Saving corrections to memory..."):
            try:
                save_response = api.save_corrections(
                    file_id=st.session_state.uploaded_file_id,
                    mapped_rows=edited_rows,
                )
            except APIError as exc:
                st.error(str(exc))
                if exc.details:
                    st.caption(exc.details)
            else:
                if save_response.get("success", False):
                    mark_saved(edited_rows)
                    st.success("Changes saved.")
                    st.rerun()
                else:
                    st.error("Corrections were not saved.")
                    for error in save_response.get("errors", []):
                        st.error(error)

with action_col3:
    if st.session_state.export_file:
        st.download_button(
            "📥 Download Excel",
            data=st.session_state.export_file["content"],
            file_name=st.session_state.export_file["filename"],
            mime=EXCEL_MIME_TYPE,
            use_container_width=True,
        )
    elif st.button("📥 Download Excel", disabled=not rows, use_container_width=True):
        with st.spinner("Preparing Excel export..."):
            try:
                content, filename = api.export_excel(
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
                st.session_state.export_file = {
                    "content": content,
                    "filename": filename,
                }
                st.success("Excel file is ready.")

with st.expander("Metadata", expanded=False):
    st.json(meta)

with st.expander("Raw backend response", expanded=False):
    st.json(response)
