"""FastAPI server for screenshot service"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Optional
from .service import ScreenshotService
from ..cli import PRESETS

app = FastAPI(
    title="Screenshot Control API",
    description="Web screenshot service with multiple presets and formats",
    version="0.1.0"
)

screenshot_service = ScreenshotService()

class ScreenshotRequest(BaseModel):
    url: HttpUrl
    preset: Optional[str] = "desktop"
    width: Optional[int] = None
    height: Optional[int] = None
    format: Optional[str] = "base64"
    full_page: Optional[bool] = False

@app.get("/presets")
async def get_presets():
    """List available screen size presets"""
    preset_info = "Available screen size presets:\n"
    preset_info += f"{'NAME':12} {'SIZE':12} DESCRIPTION\n"
    preset_info += "-" * 50 + "\n"
    
    for name, (w, h, desc) in PRESETS.items():
        preset_info += f"{name:12} {w}x{h:<12} {desc}\n"
    
    return {"presets": preset_info}

@app.post("/screenshot")
async def take_screenshot(request: ScreenshotRequest):
    """Take a screenshot of the specified URL"""
    if request.preset not in PRESETS and not (request.width and request.height):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid preset. Must be one of: {', '.join(PRESETS.keys())}"
        )
    
    success, error, image = await screenshot_service.take_screenshot(
        str(request.url),
        request.preset,
        request.width,
        request.height,
        request.full_page
    )
    
    if not success:
        raise HTTPException(status_code=500, detail=error)
    
    if request.format == "binary":
        return Response(
            content=image,
            media_type="image/png"
        )
    
    return {
        "success": True,
        "image": image
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
