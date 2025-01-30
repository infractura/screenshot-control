"""API documentation configuration"""
from fastapi.openapi.utils import get_openapi

# API metadata
API_TITLE = "Screenshot Control API"
API_VERSION = "1.0.0"
API_DESCRIPTION = """
A powerful web screenshot utility with multiple interfaces.

Features:
- Multiple screen size presets (desktop, laptop, tablet, phone)
- Full page scrolling capture
- Base64 or binary responses
- Custom viewport sizes
"""

# API tags metadata
API_TAGS = [
    {
        "name": "screenshots",
        "description": "Operations with screenshots",
    },
    {
        "name": "presets",
        "description": "Screen size preset operations",
    },
]

def get_openapi_schema(app):
    """Generate custom OpenAPI schema"""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=API_TITLE,
        version=API_VERSION,
        description=API_DESCRIPTION,
        routes=app.routes,
    )

    # Add security schemes if needed
    # openapi_schema["components"]["securitySchemes"] = {...}

    # Custom tags metadata
    openapi_schema["tags"] = API_TAGS

    app.openapi_schema = openapi_schema
    return app.openapi_schema
