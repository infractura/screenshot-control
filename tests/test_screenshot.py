import pytest
import os
from screenshot_control.cli import (
    is_url,
    sanitize_filename,
    get_output_path,
    PRESETS
)
from screenshot_control.client.screenshot_client import ScreenshotClient

def test_is_url():
    """Test URL validation"""
    assert is_url("https://example.com")
    assert is_url("http://sub.example.com/path")
    assert not is_url("not-a-url")
    assert not is_url("http://")

def test_sanitize_filename():
    """Test filename sanitization"""
    url = "https://example.com/path/to/page?query=1"
    filename = sanitize_filename(url)
    assert "example.com_path_to_page" in filename
    assert filename.endswith(".png")
    assert not any(c in filename for c in r'?/\:*"<>|')

def test_get_output_path():
    """Test output path generation"""
    url = "https://example.com"
    
    # Test with no output specified
    path = get_output_path(url, None)
    assert path.endswith(".png")
    assert "example.com" in path
    
    # Test with directory
    path = get_output_path(url, "test_dir/")
    assert path.startswith("test_dir/")
    assert path.endswith(".png")
    
    # Test with filename
    path = get_output_path(url, "test.png")
    assert path == "test.png"

def test_presets():
    """Test screen size presets"""
    assert "desktop" in PRESETS
    assert "phone" in PRESETS
    assert len(PRESETS["desktop"]) == 3
    width, height, desc = PRESETS["desktop"]
    assert isinstance(width, int)
    assert isinstance(height, int)
    assert isinstance(desc, str)

@pytest.mark.asyncio
async def test_screenshot_client():
    """Test screenshot client"""
    client = ScreenshotClient()
    
    # Test health check
    health = await client.health_check()
    assert health["status"] == "healthy"
    
    # Test presets
    presets = await client.get_presets()
    assert "presets" in presets
    
    # Test taking screenshot
    output_path = "test_screenshot.png"
    try:
        result = await client.get_screenshot(
            "https://example.com",
            preset="phone",
            output_path=output_path
        )
        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0
    finally:
        if os.path.exists(output_path):
            os.remove(output_path)
