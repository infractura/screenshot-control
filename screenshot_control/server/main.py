"""FastAPI server for screenshot service"""
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, Dict, Any
import os
from pathlib import Path

from .service import ScreenshotService
from ..cli import PRESETS
from . import api_docs

# Get the current directory
BASE_DIR = Path(__file__).resolve().parent

# Create the FastAPI app
app = FastAPI(
    title="Screenshot Control API",
    description="""
    A powerful web screenshot utility with multiple interfaces.
    
    Features:
    - Multiple screen size presets (desktop, laptop, tablet, phone)
    - Full page scrolling capture
    - Base64 or binary responses
    - Custom viewport sizes
    """,
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
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

class PresetResponse(BaseModel):
    """Response model for preset information"""
    presets: Dict[str, Dict[str, Any]] = Field(
        ...,
        description="Dictionary of available presets with their configurations",
        example={
            "desktop": {
                "width": 1920,
                "height": 1080,
                "description": "Desktop HD"
            }
        }
    )

class ScreenshotRequest(BaseModel):
    """Request model for taking screenshots"""
    url: HttpUrl = Field(
        ...,
        description="URL of the webpage to capture",
        example="https://example.com"
    )
    preset: Optional[str] = Field(
        "desktop",
        description="Screen size preset to use",
        example="desktop"
    )
    width: Optional[int] = Field(
        None,
        description="Custom viewport width in pixels",
        gt=0,
        example=1920
    )
    height: Optional[int] = Field(
        None,
        description="Custom viewport height in pixels",
        gt=0,
        example=1080
    )
    format: Optional[str] = Field(
        "base64",
        description="Response format (base64 or binary)",
        example="base64"
    )
    full_page: Optional[bool] = Field(
        False,
        description="Whether to capture the full scrollable page",
        example=False
    )

class ScreenshotResponse(BaseModel):
    """Response model for screenshot requests"""
    success: bool = Field(
        ...,
        description="Whether the screenshot was successful",
        example=True
    )
    image: str = Field(
        ...,
        description="Base64 encoded screenshot image",
        example="iVBORw0KGgoAAAANSUhEUgAA..."
    )

class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(
        ...,
        description="Current service status",
        example="healthy"
    )

@app.get("/", tags=["web"])
async def home(request: Request):
    """Render the web interface home page"""
    return templates.TemplateResponse(
        "pages/screenshot.html",
        {"request": request}
    )

@app.get(
    "/api/presets",
    response_model=PresetResponse,
    tags=["presets"],
    summary="Get Available Presets",
    description="Returns a list of available screen size presets with their configurations"
)
async def get_presets():
    """List available screen size presets"""
    preset_info = {}
    for name, (width, height, desc) in PRESETS.items():
        preset_info[name] = {
            "width": width,
            "height": height,
            "description": desc
        }
    
    return {"presets": preset_info}

@app.post(
    "/api/screenshot",
    response_model=ScreenshotResponse,
    tags=["screenshots"],
    summary="Take Screenshot",
    description="""
    Takes a screenshot of the specified URL using either a preset or custom dimensions.
    Returns the screenshot as a base64 encoded string.
    """
)
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

@app.get(
    "/api/health",
    response_model=HealthResponse,
    tags=["system"],
    summary="Health Check",
    description="Check if the service is healthy and responding to requests"
)
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

# Apply custom OpenAPI schema
def custom_openapi():
    return api_docs.get_openapi_schema(app)

app.openapi = custom_openapi
