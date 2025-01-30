# Screenshot Control

A powerful web screenshot utility with CLI, API, and Python library interfaces. Supports multiple screen sizes, full-page captures, and various output formats.

## Features

- Multiple interfaces (CLI, API, Python library)
- Screen size presets (desktop, laptop, tablet, phone)
- Full page scrolling capture
- Basic auth support
- Directory or file output
- Base64 or binary responses
- Automatic file naming
- Headless Chrome backend

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install the package
pip install .
```

## Usage

### As CLI Tool

```bash
# Take desktop screenshot
screenshot https://example.com

# Use phone preset
screenshot -p phone https://example.com

# Save to specific directory
screenshot URL -o ~/screenshots/

# Full page capture
screenshot --full-page https://example.com
```

### As API Service

```bash
# Start the service
systemctl start screenshot-api

# Get available presets
curl http://localhost:8765/presets

# Take a screenshot
curl -X POST http://localhost:8765/screenshot \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "preset": "phone",
    "format": "base64"
  }'
```

### As Python Library

```python
from screenshot_control import ScreenshotClient

client = ScreenshotClient()
result = await client.get_screenshot(
    "https://example.com",
    preset="phone",
    output_path="~/screenshots/"
)
```

## Screen Size Presets

- desktop: 1920x1080 (Desktop HD)
- laptop: 1366x768 (Laptop)
- tablet: 768x1024 (iPad/Tablet)
- phone: 390x844 (iPhone 12/13/14)
- phone-ls: 844x390 (iPhone Landscape)
- 4k: 3840x2160 (4K Display)

## Configuration

The service can be configured through environment variables:

- `SCREENSHOT_PORT`: API service port (default: 8765)
- `SCREENSHOT_HOST`: API service host (default: localhost)
- `SCREENSHOT_TIMEOUT`: Page load timeout in seconds (default: 30)
- `SCREENSHOT_CHROME_PATH`: Custom Chrome binary path

## Development

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run linting
pylint screenshot_control

# Build documentation
mkdocs build
```

## License

MIT License - see LICENSE file for details

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

- Issue Tracker: GitHub Issues
- Documentation: https://screenshot.w12.com/docs/
