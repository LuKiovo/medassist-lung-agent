from fastapi import APIRouter, File, UploadFile

from medassist_lung_agent.imaging.chest_xray import analyze_xray_bytes


router = APIRouter()


@router.post("/analyze")
async def analyze_xray(file: UploadFile = File(...)):
    image_bytes = await file.read()
    return analyze_xray_bytes(image_bytes, filename=file.filename or "upload")

