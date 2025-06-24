# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a personal faceless video automation tool for creating social media content (slideshows/listicles) for YouTube and TikTok. The goal is to build a simple web application that generates image-based slideshows with text overlays from topic inputs.

## Environment Setup

The project uses Python with a virtual environment located at `./venv/`. 

**Activate virtual environment:**
```bash
source venv/bin/activate
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

## Dependencies

The project currently includes AI/ML dependencies for image generation:
- `diffusers==0.34.0` - Hugging Face diffusion models
- `torch==2.2.2` - PyTorch for ML operations
- `torchvision==0.17.2` - Computer vision utilities
- `transformers==4.46.3` - Transformer models
- `accelerate==1.0.1` - Accelerated training/inference
- `safetensors==0.5.3` - Safe tensor serialization
- Plus supporting libraries (numpy, pillow, etc.)

## Project Structure

```
faceless-video-automation/
├── stable-diffusion/          # AI image generation
│   ├── models/               # Model storage (empty initially)
│   ├── outputs/              # Generated images
│   └── scripts/              # Generation scripts
├── assets/                   # Static assets
├── automation-workflows/     # Workflow definitions
├── ffmpeg-scripts/          # Video processing scripts
├── temp/                    # Temporary files
└── requirements.txt         # Python dependencies
```

## Development Commands

**Run image generation:**
```bash
# Navigate to stable-diffusion scripts
cd stable-diffusion/scripts/
python generate_images.py
```

**Process videos with FFmpeg:**
```bash
# Navigate to ffmpeg scripts
cd ffmpeg-scripts/
# Run specific video processing script
```

## Architecture Notes

The application is designed for local development on M2 Max MacBook Pro with 64GB RAM, optimized for:
- Local Stable Diffusion inference
- Video processing with FFmpeg
- Manual content creation workflow (not automated)

## Planned Tech Stack

**Backend:** Python Flask/FastAPI for API endpoints
**Frontend:** Next.js for simple form interface
**Image Generation:** Stable Diffusion via diffusers library
**Video Assembly:** FFmpeg for slideshow creation
**Text Generation:** Transformers for content generation

## Git Ignore

The project excludes:
- `stable-diffusion/models/` (large model files)
- `temp/` (temporary processing files)
- `*.mp4` (generated video files)

## Development Workflow

1. Generate images using Stable Diffusion scripts
2. Process text overlays and combine images
3. Use FFmpeg to create final slideshow videos
4. Manual review and download of results

This is a personal tool focused on simplicity and local processing power rather than scalability or automation.