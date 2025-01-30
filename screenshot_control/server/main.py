"""FastAPI server for screenshot service"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, HttpUrl
from typing import Optional
import os
from pathlib import Path

from .service import ScreenshotService
from ..cli import PRESETS

# Get the current directory
BASE_DIR = Path(__file__).resolve().parent

# Create the FastAPI app
app = FastAPI(
    title="Screenshot Control API",
    description="Web screenshot service with multiple presets and formats",
    version="0.1.0"
)

# Mount static files
app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static"
)

# Templates
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Initialize screenshot service
screenshot_service = ScreenshotService()

class ScreenshotRequest(BaseModel):
    url: HttpUrl
    preset: Optional[str] = "desktop"
    width: Optional[int] = None
    height: Optional[int] = None
    format: Optional[str] = "base64"
    full_page: Optional[bool] = False

@app.get("/")
async def home(request: Request):
    """Render the home page"""
    return templates.TemplateResponse(
        "pages/screenshot.html",
        {"request": request}
    )

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
    
    return {
        "success": True,
        "image": image
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
