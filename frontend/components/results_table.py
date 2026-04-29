from __future__ import annotations

from typing import Any, Dict, List, Tuple

import pandas as pd
import streamlit as st

from state import dataframe_to_records, diff_records, records_to_dataframe


def render_editable_results_table(
    original_rows: List[Dict[str, Any]],
    edited_rows: List[Dict[str, Any]],
    key: str,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    dataframe = records_to_dataframe(edited_rows or original_rows)

    if dataframe.empty:
        st.info("No mapped rows were returned by the AI pipeline.")
        return [], []

    st.caption("Review the mapped rows below. You can edit cells and add or remove rows.")

    edited_dataframe = st.data_editor(
        dataframe,
        key=key,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
    )

    current_rows = dataframe_to_records(edited_dataframe)
    changes = diff_records(original_rows, current_rows)

    col1, col2, col3 = st.columns(3)
    col1.metric("Rows", len(current_rows))
    col2.metric("Columns", len(edited_dataframe.columns))
    col3.metric("Edited cells", len(changes))

    if changes:
        st.info("Edited cells are tracked locally until you save corrections.")
        with st.expander("View edited cells", expanded=False):
            st.dataframe(pd.DataFrame(changes), use_container_width=True, hide_index=True)

        with st.expander("Highlighted edited table", expanded=False):
            st.dataframe(
                _highlight_changes(edited_dataframe, changes),
                use_container_width=True,
                hide_index=True,
            )
    else:
        st.success("No unsaved edits.")

    return current_rows, changes


def _highlight_changes(
    dataframe: pd.DataFrame,
    changes: List[Dict[str, Any]],
) -> Any:
    styles = pd.DataFrame("", index=dataframe.index, columns=dataframe.columns)

    for change in changes:
        row_index = int(change["row"]) - 1
        column = change["field"]

        if row_index in styles.index and column in styles.columns:
            styles.loc[row_index, column] = "background-color: #fff3cd"

    return dataframe.style.apply(lambda _: styles, axis=None)
