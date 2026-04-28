from fastapi import APIRouter
import os

router = APIRouter()

SCHEMA_DIR = "app/schemas/mapping_profiles"


@router.get("/")
def list_schemas():
    try:
        files = [f for f in os.listdir(SCHEMA_DIR) if f.endswith(".json")]

        return {"success": True, "data": files, "errors": []}

    except Exception as e:
        return {"success": False, "data": None, "errors": [str(e)]}


@router.get("/{schema_name}")
def get_schema(schema_name: str):
    try:
        path = os.path.join(SCHEMA_DIR, schema_name)

        if not os.path.exists(path):
            return {"success": False, "data": None, "errors": ["Schema not found"]}

        import json

        with open(path, "r") as f:
            schema = json.load(f)

        return {"success": True, "data": schema, "errors": []}

    except Exception as e:
        return {"success": False, "data": None, "errors": [str(e)]}
