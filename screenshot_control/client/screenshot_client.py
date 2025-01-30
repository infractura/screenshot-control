"""Screenshot Control Client Library"""
import os
import base64
import aiohttp
from typing import Optional, Union, Dict
from urllib.parse import urljoin

class ScreenshotClient:
    """Client for interacting with Screenshot Control API"""
    
    def __init__(self, base_url: str = "http://localhost:8765"):
        """Initialize client with API base URL"""
        self.base_url = base_url.rstrip('/')
        
    async def get_presets(self) -> Dict[str, str]:
        """Get available screen size presets"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/presets") as response:
                if response.status == 200:
                    return await response.json()
                raise Exception(f"Failed to get presets: {response.status}")

    async def get_screenshot(
        self,
        url: str,
        preset: str = "desktop",
        width: Optional[int] = None,
        height: Optional[int] = None,
        output_path: Optional[str] = None,
        format: str = "base64",
        full_page: bool = False
    ) -> Union[str, bytes]:
        """
        Take a screenshot of the specified URL
        
        Args:
            url: Website URL to capture
            preset: Screen size preset (desktop, laptop, tablet, phone, etc)
            width: Custom viewport width (overrides preset)
            height: Custom viewport height (overrides preset)
            output_path: Path to save the screenshot
            format: Response format (base64 or binary)
            full_page: Whether to capture full scrolling page
            
        Returns:
            base64 string or binary image data
        """
        data = {
            "url": url,
            "preset": preset,
            "format": format,
            "full_page": full_page
        }
        
        if width and height:
            data["width"] = width
            data["height"] = height
            
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/screenshot",
                json=data
            ) as response:
                if response.status != 200:
                    raise Exception(
                        f"Screenshot failed: {response.status}"
                    )
                
                if format == "binary":
                    image_data = await response.read()
                else:
                    result = await response.json()
                    image_data = base64.b64decode(result["image"])
                
                if output_path:
                    # Expand user path
                    output_path = os.path.expanduser(output_path)
                    
                    # Create directory if it doesn't exist
                    os.makedirs(
                        os.path.dirname(os.path.abspath(output_path)),
                        exist_ok=True
                    )
                    
                    # Save the image
                    with open(output_path, 'wb') as f:
                        f.write(image_data)
                    
                    return output_path
                
                return image_data

    async def health_check(self) -> Dict[str, str]:
        """Check if the service is healthy"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    return await response.json()
                raise Exception(f"Health check failed: {response.status}")
