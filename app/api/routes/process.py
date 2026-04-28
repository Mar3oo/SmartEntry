from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from app.core.contracts import PipelineInput
from app.dependencies import get_orchestrator

from app.services.exports.excel_exporter import ExcelExporter
from fastapi.responses import FileResponse

router = APIRouter()


# 🔥 Updated request (now supports profile)
class ProcessRequest(BaseModel):
    file_id: str
    file_path: str
    file_type: str
    profile: Optional[str] = "generic_excel.json"


@router.post("/")
def process_file(request: ProcessRequest):
    # 🔥 Get orchestrator
    orchestrator, _ = get_orchestrator()

    # 🔥 Build mapping agent dynamically
    profile_path = f"app/schemas/mapping_profiles/{request.profile}"

    from app.agents.mapping_agent import MappingAgent

    mapping_agent = MappingAgent(profile_path)

    # 🔥 Build pipeline input
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
        "meta": {"profile_used": request.profile},
    }


@router.post("/excel/")
def process_to_excel(request: ProcessRequest):
    orchestrator, _ = get_orchestrator()

    # 🔥 Dynamic profile selection
    profile_path = f"app/schemas/mapping_profiles/{request.profile}"

    from app.agents.mapping_agent import MappingAgent

    mapping_agent = MappingAgent(profile_path)

    input_data = PipelineInput(
        file_id=request.file_id,
        file_path=request.file_path,
        file_type=request.file_type,
    )

    state = orchestrator.run(input_data, mapping_agent)

    if state.errors:
        return {"success": False, "errors": state.errors}

    exporter = ExcelExporter()
    file_path = f"data/processed/{request.file_id}.xlsx"

    exporter.export(state.mapped_data, file_path)

    return FileResponse(
        path=file_path,
        filename="invoice.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
