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


class MappingAgent(BaseAgent):
    def __init__(self, profile_path: str):
        super().__init__("mapping_agent")
        self.profile_path = profile_path

        with open(profile_path, "r") as f:
            self.mapping = json.load(f)

    def _run(self, state: PipelineState) -> PipelineState:
        if not state.validated_data:
            state.errors.append("No validated data to map")
            return state

        mapped = {}

        for target_field, source_path in self.mapping.items():
            mapped[target_field] = get_value(state.validated_data, source_path)

        state.mapped_data = mapped

        return state
