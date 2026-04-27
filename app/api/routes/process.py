from fastapi import APIRouter
from pydantic import BaseModel

from app.core.contracts import PipelineInput
from app.dependencies import get_orchestrator

router = APIRouter()


class ProcessRequest(BaseModel):
    file_id: str
    file_path: str
    file_type: str


@router.post("/")
def process_file(request: ProcessRequest):
    orchestrator, mapping_agent = get_orchestrator()

    input_data = PipelineInput(
        file_id=request.file_id,
        file_path=request.file_path,
        file_type=request.file_type,
    )

    state = orchestrator.run(input_data, mapping_agent)

    return {
        "success": len(state.errors) == 0,
        "data": state.mapped_data,
        "errors": state.errors,
        "meta": None,
    }
