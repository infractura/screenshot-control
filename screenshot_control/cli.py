#!/usr/bin/env python3
"""Command line interface for taking web screenshots with various screen sizes and options."""

import argparse
import io
import os
import re
import sys
import time
from datetime import datetime
from urllib.parse import urlparse

from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

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
    """Display available screen size presets."""
    print("\nAvailable screen size presets:")
    print(f"{'NAME':12} {'SIZE':12} DESCRIPTION")
    print("-" * 50)
    for name, (w, h, desc) in PRESETS.items():
        print(f"{name:12} {w}x{h:<12} {desc}")
    print()

def is_url(string):
    """Check if string is URL."""
    try:
        result = urlparse(string)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def sanitize_filename(url):
    """Convert URL to safe filename."""
    parsed = urlparse(url)
    hostname = parsed.netloc.split('@')[-1]
    base = f"{hostname}{parsed.path}".rstrip('/')
    safe = re.sub(r'[^a-zA-Z0-9._-]', '_', base)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{safe}_{timestamp}.png"

def get_output_path(url, output_arg):
    """Generate output path based on URL and output argument."""
    if not output_arg:
        return sanitize_filename(url)

    output_path = os.path.expanduser(output_arg)

    if os.path.isdir(output_path) or output_path.endswith('/'):
        filename = sanitize_filename(url)
        return os.path.join(output_path, filename)

    return output_path

class ScreenshotConfig:
    """Configuration for web screenshot capture."""
    def __init__(self, width=1920, height=1080, wait=2, full_page=False):
        self.width = width
        self.height = height
        self.wait = wait
        self.full_page = full_page

    def get_window_size_arg(self):
        """Get the window size argument for webdriver."""
        return f"--window-size={self.width},{self.height}"

    @classmethod
    def from_preset(cls, preset_name):
        """Create config from a preset name."""
        width, height, _ = PRESETS[preset_name]
        return cls(width=width, height=height)

def setup_webdriver(config):
    """Setup and return configured webdriver."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument(config.get_window_size_arg())
    options.add_argument("--no-sandbox")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def get_page_height(driver):
    """Get total height of the page."""
    return driver.execute_script("""
        return Math.max(
            document.body.scrollHeight,
            document.documentElement.scrollHeight,
            document.body.offsetHeight,
            document.documentElement.offsetHeight
        );
    """)

def take_screenshot(driver):
    """Take a screenshot using the webdriver."""
    screenshot_data = driver.get_screenshot_as_png()
    return Image.open(io.BytesIO(screenshot_data))

def capture_full_page(driver, config):
    """Capture full page screenshot by scrolling."""
    total_height = get_page_height(driver)
    viewport_height = driver.execute_script("return window.innerHeight")
    num_screenshots = -(-total_height // viewport_height)
    screenshots = []

    for i in range(num_screenshots):
        scroll_pos = i * viewport_height
        driver.execute_script(f"window.scrollTo(0, {scroll_pos})")
        time.sleep(0.2)
        screenshots.append(take_screenshot(driver))

    final_image = Image.new('RGB', (config.width, total_height))

    for i, screenshot in enumerate(screenshots):
        paste_height = i * viewport_height
        is_last = i == num_screenshots - 1
        crop_height = total_height - paste_height if is_last else viewport_height
        cropped = screenshot.crop((0, 0, config.width, crop_height))
        final_image.paste(cropped, (0, paste_height))

    return final_image

def web_screenshot(url, output_path=None, config=None):
    """Take screenshot of webpage with optional full page capture.
    
    Args:
        url: The URL to capture
        output_path: Optional path to save the screenshot
        config: ScreenshotConfig object, uses defaults if None
    
    Returns:
        Tuple of (success, output_path)
    """
    try:
        if config is None:
            config = ScreenshotConfig()
        output_path = get_output_path(url, output_path)
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        driver = setup_webdriver(config)
        driver.get(url)
        time.sleep(config.wait)

        if not config.full_page:
            driver.save_screenshot(output_path)
            driver.quit()
            return True, output_path

        final_image = capture_full_page(driver, config)
        final_image.save(output_path, 'PNG')
        driver.quit()
        return True, output_path

    except (WebDriverException, IOError) as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return False, None

def create_parser():
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        description='Capture webpage screenshots at various screen sizes'
    )

    doc_group = parser.add_argument_group('documentation')
    doc_group.add_argument('--readme', action='store_true', help='Show README')
    doc_group.add_argument('--api-spec', action='store_true', help='Show API specification')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('url', nargs='?', help='URL to capture')
    group.add_argument(
        '-l', '--list',
        action='store_true',
        help='List available screen size presets'
    )

    parser.add_argument('-o', '--output', help='Output filename or directory')
    parser.add_argument(
        '-p', '--preset',
        choices=PRESETS.keys(),
        default='desktop',
        help='Screen size preset (default: desktop)'
    )
    parser.add_argument('--width', type=int, help='Custom viewport width')
    parser.add_argument('--height', type=int, help='Custom viewport height')
    parser.add_argument('--wait', type=float, default=2,
                       help='Seconds to wait for page load (default: 2)')
    parser.add_argument('-q', '--quiet', action='store_true',
                       help='Only output filename on success')
    parser.add_argument('--full-page', action='store_true',
                       help='Capture full scrolling page')
    return parser

def main():
    """Main entry point for the CLI."""
    parser = create_parser()

    args = parser.parse_args()

    if args.list:
        list_presets()
        sys.exit(0)

    if not args.url:
        parser.print_help()
        sys.exit(1)

    if not is_url(args.url):
        print(f"Error: Invalid URL: {args.url}", file=sys.stderr)
        sys.exit(1)

    # Create screenshot configuration
    if args.width and args.height:
        config = ScreenshotConfig(
            width=args.width,
            height=args.height,
            wait=args.wait,
            full_page=args.full_page
        )
    else:
        config = ScreenshotConfig.from_preset(args.preset)
        config.wait = args.wait
        config.full_page = args.full_page

    success, output_path = web_screenshot(
        args.url,
        args.output,
        config
    )

    if success:
        if args.quiet:
            print(output_path)
        else:
            print(f"\nScreenshot saved to: {os.path.abspath(output_path)}\n")
        sys.exit(0)
    sys.exit(1)

if __name__ == "__main__":
    main()
