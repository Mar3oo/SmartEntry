from fastapi import APIRouter

from app.api.routes import upload, process, schema, memory

api_router = APIRouter()

api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
api_router.include_router(process.router, prefix="/process", tags=["process"])
api_router.include_router(schema.router, prefix="/schema", tags=["schema"])
api_router.include_router(memory.router, prefix="/memory", tags=["memory"])
