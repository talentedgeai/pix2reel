# Pix2Reel: Image to Reel Generator

## Overview

Pix2Reel is a Python library that transforms a collection of images into engaging video reels with customizable text overlays and audio integration.

## Features

- Convert multiple images into a vertical video reel
- Add custom text overlays to each image
- Synchronize with background audio
- Compatible with social media vertical video formats (1080x1920)

## Prerequisites

- Python 3.6+
- FFmpeg installed on your system
- pip

## Installation

```bash
pip install pix2reel
```

## Quick Start

```python
from pix2reel import run_reel_assembly

# Prepare your inputs
images = ["image1.jpg", "image2.jpg", "image3.jpg", "image4.jpg"]
texts = ["First Caption", "Second Caption", "Third Caption", "Fourth Caption"]
audio_file = "background_music.mp3"
output_video = "my_reel.mp4"

# Generate your reel
run_reel_assembly(images, texts, audio_file, output_video)
```

## Parameters

- `images`: List of image file paths
- `texts`: List of text captions (same length as images)
- `audio_file`: Background music file
- `output_video`: Output video file path
- `segment_durations`: Custom timing for each image

## Customization

- Adjust image display duration
- Modify text styling
- Control audio volume

## Requirements

- requests
- openai

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

MIT License

## Author

Khang Nguyen
khang.nguyen@talentedge.ai