#!/usr/bin/env python3

import sys
import os
import re
import time
from datetime import datetime
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import io

# Screen size presets
PRESETS = {
    'desktop': (1920, 1080, "Desktop HD"),
    'laptop': (1366, 768, "Laptop"),
    'tablet': (768, 1024, "iPad/Tablet"),
    'phone': (390, 844, "iPhone 12/13/14"),
    'phone-ls': (844, 390, "iPhone Landscape"),
    '4k': (3840, 2160, "4K Display"),
}

def list_presets():
    """Display available screen size presets"""
    print("\nAvailable screen size presets:")
    print(f"{'NAME':12} {'SIZE':12} DESCRIPTION")
    print("-" * 50)
    for name, (w, h, desc) in PRESETS.items():
        print(f"{name:12} {w}x{h:<12} {desc}")
    print()

def is_url(string):
    """Check if string is URL"""
    try:
        result = urlparse(string)
        return all([result.scheme, result.netloc])
    except:
        return False

def sanitize_filename(url):
    """Convert URL to safe filename"""
    parsed = urlparse(url)
    hostname = parsed.netloc.split('@')[-1]
    base = f"{hostname}{parsed.path}".rstrip('/')
    safe = re.sub(r'[^a-zA-Z0-9._-]', '_', base)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{safe}_{timestamp}.png"

def get_output_path(url, output_arg):
    """Generate output path based on URL and output argument"""
    if not output_arg:
        return sanitize_filename(url)
    
    # Expand user path (~/)
    output_path = os.path.expanduser(output_arg)
    
    # If it's a directory, generate filename inside it
    if os.path.isdir(output_path) or output_path.endswith('/'):
        filename = sanitize_filename(url)
        return os.path.join(output_path, filename)
    
    # If it's a file path, use it as is
    return output_path

def web_screenshot(url, output_path=None, width=1920, height=1080, wait=2, full_page=False):
    """Take screenshot of webpage with optional full page capture"""
    try:
        output_path = get_output_path(url, output_path)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        options = Options()
        options.add_argument("--headless")
        options.add_argument(f"--window-size={width},{height}")
        options.add_argument("--no-sandbox")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        driver.get(url)
        time.sleep(wait)

        if not full_page:
            driver.save_screenshot(output_path)
            driver.quit()
            return True, output_path

        # Get page dimensions
        total_height = driver.execute_script("""
            return Math.max(
                document.body.scrollHeight,
                document.documentElement.scrollHeight,
                document.body.offsetHeight,
                document.documentElement.offsetHeight
            );
        """)

        # Calculate number of screenshots needed
        viewport_height = driver.execute_script("return window.innerHeight")
        num_screenshots = -(-total_height // viewport_height)  # Ceiling division
        
        # Take screenshots
        screenshots = []
        for i in range(num_screenshots):
            driver.execute_script(f"window.scrollTo(0, {i * viewport_height})")
            time.sleep(0.2)  # Small delay for scroll animations
            screenshot = Image.open(io.BytesIO(driver.get_screenshot_as_png()))
            screenshots.append(screenshot)

        # Create final image
        final_image = Image.new('RGB', (width, total_height))
        
        # Stitch screenshots together
        for i, screenshot in enumerate(screenshots):
            paste_height = i * viewport_height
            # Crop to remove potential overlaps
            if i == num_screenshots - 1:  # Last screenshot
                crop_height = total_height - paste_height
            else:
                crop_height = viewport_height
            cropped = screenshot.crop((0, 0, width, crop_height))
            final_image.paste(cropped, (0, paste_height))

        # Save final image
        final_image.save(output_path, 'PNG')
        driver.quit()
        return True, output_path

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return False, None

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Capture webpage screenshots at various screen sizes')
    
    # Documentation flags
    doc_group = parser.add_argument_group('documentation')
    doc_group.add_argument('--readme', action='store_true', help='Show README')
    doc_group.add_argument('--api-spec', action='store_true', help='Show API specification')
    
    # Create a group for list-presets to be exclusive with URL
    group = parser.add_mutually_exclusive_group()
    group.add_argument('url', nargs='?', help='URL to capture')
    group.add_argument('-l', '--list', action='store_true', help='List available screen size presets')
    
    parser.add_argument('-o', '--output', help='Output filename or directory')
    parser.add_argument('-p', '--preset', choices=PRESETS.keys(), 
                       default='desktop', help='Screen size preset (default: desktop)')
    parser.add_argument('--width', type=int, help='Custom viewport width')
    parser.add_argument('--height', type=int, help='Custom viewport height')
    parser.add_argument('--wait', type=float, default=2, 
                       help='Seconds to wait for page load (default: 2)')
    parser.add_argument('-q', '--quiet', action='store_true', 
                       help='Only output filename on success')
    parser.add_argument('--full-page', action='store_true',
                       help='Capture full scrolling page')
    
    args = parser.parse_args()

    # Handle --list
    if args.list:
        list_presets()
        sys.exit(0)
    
    # Check if URL is provided
    if not args.url:
        parser.print_help()
        sys.exit(1)
    
    # Validate URL
    if not is_url(args.url):
        print(f"Error: Invalid URL: {args.url}", file=sys.stderr)
        sys.exit(1)
    
    # Get dimensions from preset or custom values
    if args.width and args.height:
        width, height = args.width, args.height
    else:
        width, height, _ = PRESETS[args.preset]
    
    success, output_path = web_screenshot(
        args.url, 
        args.output, 
        width, 
        height, 
        args.wait,
        args.full_page
    )
    
    if success:
        if args.quiet:
            print(output_path)
        else:
            print(f"\nScreenshot saved to: {os.path.abspath(output_path)}\n")
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
