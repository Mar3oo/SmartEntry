from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional

try:
    import streamlit as st
except Exception:  # pragma: no cover - allows data helpers to be imported in tests
    st = None


SESSION_DEFAULTS: Dict[str, Any] = {
    "schema_config": {
        "profile": "generic_excel",
        "currency": "USD",
        "date_format": "YYYY-MM-DD",
    },
    "selected_file_signature": None,
    "uploaded_file": None,
    "uploaded_file_id": None,
    "uploaded_file_path": None,
    "uploaded_file_name": None,
    "uploaded_file_type": None,
    "upload_response": None,
    "processed_response": None,
    "original_rows": [],
    "edited_rows": [],
    "results_editor_version": 0,
    "last_saved_at": None,
    "save_feedback": None,
    "export_file": None,
}


def init_session_state() -> None:
    for key, default in SESSION_DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = deepcopy(default)


def file_signature(uploaded_file: Any) -> Optional[str]:
    if uploaded_file is None:
        return None

    return ":".join(
        [
            getattr(uploaded_file, "name", ""),
            str(getattr(uploaded_file, "size", "")),
            getattr(uploaded_file, "type", ""),
        ]
    )


def reset_for_selected_file(uploaded_file: Any) -> None:
    signature = file_signature(uploaded_file)

    if st.session_state.selected_file_signature == signature:
        st.session_state.uploaded_file = uploaded_file
        return

    st.session_state.selected_file_signature = signature
    st.session_state.uploaded_file = uploaded_file
    st.session_state.uploaded_file_id = None
    st.session_state.uploaded_file_path = None
    st.session_state.uploaded_file_name = getattr(uploaded_file, "name", None)
    st.session_state.uploaded_file_type = None
    st.session_state.upload_response = None
    st.session_state.processed_response = None
    st.session_state.original_rows = []
    st.session_state.edited_rows = []
    st.session_state.last_saved_at = None
    st.session_state.save_feedback = None
    st.session_state.export_file = None
    st.session_state.results_editor_version += 1


def current_profile() -> str:
    config = st.session_state.get("schema_config", {})
    return config.get("profile", "generic_excel")


def set_processed_response(response: Dict[str, Any]) -> None:
    rows = rows_from_response_data(response.get("data"))
    st.session_state.processed_response = response
    st.session_state.original_rows = deepcopy(rows)
    st.session_state.edited_rows = deepcopy(rows)
    st.session_state.last_saved_at = None
    st.session_state.save_feedback = None
    st.session_state.export_file = None
    st.session_state.results_editor_version += 1


def mark_saved(rows: List[Dict[str, Any]]) -> None:
    st.session_state.original_rows = deepcopy(rows)
    st.session_state.edited_rows = deepcopy(rows)
    st.session_state.last_saved_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.save_feedback = "Changes saved."


def rows_from_response_data(data: Any) -> List[Dict[str, Any]]:
    if isinstance(data, list):
        return _coerce_records(data)

    if not isinstance(data, dict):
        return [{"value": data}] if data is not None else []

    mapped_data = data.get("mapped_data")
    if isinstance(mapped_data, list):
        return _coerce_records(mapped_data)

    items = data.get("items")
    if isinstance(items, list) and items:
        shared = _shared_invoice_fields(data)
        return [
            {
                **shared,
                **flatten_record(item),
            }
            for item in items
        ]

    return [flatten_record(data)]


def records_to_dataframe(rows: Iterable[Dict[str, Any]]) -> Any:
    import pandas as pd

    records = list(rows or [])
    if not records:
        return pd.DataFrame()

    return pd.DataFrame(records)


def dataframe_to_records(dataframe: Any) -> List[Dict[str, Any]]:
    records = dataframe.to_dict(orient="records")
    return [
        {str(key): _clean_value(value) for key, value in record.items()}
        for record in records
    ]


def diff_records(
    original_rows: List[Dict[str, Any]],
    edited_rows: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    changes = []
    max_rows = max(len(original_rows), len(edited_rows))

    for row_index in range(max_rows):
        original = original_rows[row_index] if row_index < len(original_rows) else {}
        edited = edited_rows[row_index] if row_index < len(edited_rows) else {}
        columns = sorted(set(original) | set(edited))

        for column in columns:
            before = original.get(column)
            after = edited.get(column)

            if _compare_value(before) != _compare_value(after):
                changes.append(
                    {
                        "row": row_index + 1,
                        "field": column,
                        "original": before,
                        "edited": after,
                    }
                )

    return changes


def flatten_record(record: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
    flattened: Dict[str, Any] = {}

    for key, value in record.items():
        column = f"{prefix}.{key}" if prefix else str(key)

        if isinstance(value, dict):
            flattened.update(flatten_record(value, column))
        elif isinstance(value, list):
            flattened[column] = json.dumps(value, ensure_ascii=False)
        else:
            flattened[column] = value

    return flattened


def _coerce_records(rows: Iterable[Any]) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []

    for row in rows:
        if isinstance(row, dict):
            records.append(row)
        else:
            records.append({"value": row})

    return records


def _shared_invoice_fields(data: Dict[str, Any]) -> Dict[str, Any]:
    shared: Dict[str, Any] = {}

    for key in ("supplier", "customer", "currency"):
        value = data.get(key)
        if value is not None:
            shared[key] = _display_value(value)

    for group in ("invoice", "totals"):
        value = data.get(group)
        if isinstance(value, dict):
            for nested_key, nested_value in value.items():
                shared[f"{group}.{nested_key}"] = _display_value(nested_value)

    return shared


def _display_value(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)

    return value


def _clean_value(value: Any) -> Any:
    if value is None:
        return None

    if _is_missing(value):
        return None

    if hasattr(value, "item"):
        try:
            return value.item()
        except (TypeError, ValueError):
            pass

    return value


def _compare_value(value: Any) -> str:
    value = _clean_value(value)
    return json.dumps(value, sort_keys=True, default=str)


def _is_missing(value: Any) -> bool:
    try:
        import pandas as pd
    except ImportError:
        pd = None

    if pd is not None:
        try:
            missing = pd.isna(value)
            if isinstance(missing, bool):
                return missing
            if hasattr(missing, "item"):
                return bool(missing.item())
        except (TypeError, ValueError):
            pass

    try:
        return bool(value != value)
    except (TypeError, ValueError):
        return False
