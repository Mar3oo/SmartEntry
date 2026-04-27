from abc import ABC, abstractmethod
from app.core.state import PipelineState


class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name

    def __call__(self, state: PipelineState) -> PipelineState:
        return self.run(state)

    def run(self, state: PipelineState) -> PipelineState:
        try:
            return self._run(state)
        except Exception as e:
            state.errors.append(f"{self.name}: {str(e)}")
            return state

    @abstractmethod
    def _run(self, state: PipelineState) -> PipelineState:
        """
        Implement agent logic here
        """
        pass
