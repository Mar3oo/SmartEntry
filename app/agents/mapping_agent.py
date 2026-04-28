import json
from typing import Any, Dict

from app.agents.base_agent import BaseAgent
from app.core.state import PipelineState


def get_value(data: Dict, path: str) -> Any:
    """
    Extract value using dot notation
    Example: "invoice.invoice_number"
    """
    keys = path.split(".")
    current = data

    for key in keys:
        if current is None:
            return None
        current = current.get(key)

    return current


def apply_value_correction(store, field: str, value: Any):
    """
    Apply learned value corrections ONLY (not schema/field names)
    Example:
    "$" → "USD"
    """
    if not store or value is None:
        return value

    key = f"value_correction:{field}:{value}"

    correction = store.get_document(key)

    if correction:
        return correction.get("correct_value", value)

    return value


class MappingAgent(BaseAgent):
    def __init__(self, profile_path: str, store=None):
        super().__init__("mapping_agent")
        self.profile_path = profile_path
        self.store = store  # 🔥 memory injected

        with open(profile_path, "r") as f:
            self.mapping = json.load(f)

    def _run(self, state: PipelineState) -> PipelineState:
        try:
            # 🔥 Always use structured_data (source of truth)
            data = state.structured_data

            if not data:
                state.errors.append("No data to map")
                return state

            print("MAPPING INPUT DATA:", data)

            items = data.get("items", [])
            rows = []

            # =========================
            # Case 1: Items exist → row per item
            # =========================
            if items:
                for item in items:
                    row = {}

                    for target_field, source_path in self.mapping.items():
                        # 🔥 Handle item-level fields
                        if source_path.startswith("item."):
                            key = source_path.replace("item.", "")
                            value = item.get(key)

                        # 🔥 Handle global fields
                        else:
                            value = get_value(data, source_path)

                        # 🔥 Apply value correction (SAFE learning)
                        value = apply_value_correction(self.store, target_field, value)

                        row[target_field] = value

                    rows.append(row)

            # =========================
            # Case 2: No items → single row
            # =========================
            else:
                row = {}

                for target_field, source_path in self.mapping.items():
                    if source_path.startswith("item."):
                        value = None
                    else:
                        value = get_value(data, source_path)

                    # 🔥 Apply value correction
                    value = apply_value_correction(self.store, target_field, value)

                    row[target_field] = value

                rows.append(row)

            state.mapped_data = rows

        except Exception as e:
            state.errors.append(f"Mapping failed: {str(e)}")

        return state
