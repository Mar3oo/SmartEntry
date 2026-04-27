from fastapi import APIRouter, UploadFile, File
import os
import uuid

router = APIRouter()

UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    # Generate unique file ID
    file_id = str(uuid.uuid4())

    # Save file
    file_path = os.path.join(UPLOAD_DIR, file_id + "_" + file.filename)

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    return {"success": True, "file_id": file_id, "file_path": file_path}
