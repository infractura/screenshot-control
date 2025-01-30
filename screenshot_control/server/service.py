"""Screenshot service wrapper"""
import os
import base64
import tempfile
from typing import Optional, Tuple
from ..cli import web_screenshot, PRESETS

class ScreenshotService:
    """Service for taking screenshots of web pages"""
    
    async def take_screenshot(
        self, 
        url: str, 
        preset: str = "desktop",
        width: Optional[int] = None,
        height: Optional[int] = None,
        full_page: bool = False
    ) -> Tuple[bool, str, Optional[str]]:
        """Take a screenshot and return the image data"""
        
        # Create temp file for output
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            temp_path = tmp.name

        try:
            # Get dimensions
            if width and height:
                w, h = width, height
            else:
                w, h, _ = PRESETS[preset]
            
            # Take screenshot
            success, output_path = web_screenshot(
                url=url,
                output_path=temp_path,
                width=w,
                height=h,
                full_page=full_page
            )
            
            if not success:
                return False, "Screenshot failed", None

            # Read the image data
            with open(temp_path, 'rb') as f:
                image_data = f.read()
            
            # Convert to base64
            b64_data = base64.b64encode(image_data).decode('utf-8')
            
            return True, "", b64_data

        except Exception as e:
            return False, f"Error: {str(e)}", None
            
        finally:
            # Cleanup temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
