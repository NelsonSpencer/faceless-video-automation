#!/usr/bin/env python3
"""
FastAPI backend for Faceless Video Automation Tool
"""

import os
import sys
import shutil
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import zipfile
import tempfile

# Add the stable-diffusion scripts to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'stable-diffusion', 'scripts'))

try:
    from generate_listicle import generate_listicle_images
except ImportError as e:
    print(f"Warning: Could not import generate_listicle: {e}")
    generate_listicle_images = None

app = FastAPI(
    title="Faceless Video Automation API",
    description="API for generating social media listicle content",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (generated images)
outputs_dir = os.path.join(os.path.dirname(__file__), '..', 'stable-diffusion', 'outputs')
if os.path.exists(outputs_dir):
    app.mount("/outputs", StaticFiles(directory=outputs_dir), name="outputs")

# Request/Response models
class ListicleRequest(BaseModel):
    topic: str
    format_type: str = "landscape"  # landscape or portrait
    background_type: str = "color"  # color, ai, or stock
    num_slides: int = 5

class ListicleResponse(BaseModel):
    success: bool
    message: str
    images: List[str] = []
    download_url: Optional[str] = None

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Faceless Video Automation API is running"}

@app.get("/formats")
async def get_formats():
    """Get available format options"""
    return {
        "formats": {
            "landscape": {
                "name": "YouTube/Landscape",
                "width": 1920,
                "height": 1080,
                "description": "Horizontal format for YouTube, Instagram posts"
            },
            "portrait": {
                "name": "TikTok/Portrait", 
                "width": 1080,
                "height": 1920,
                "description": "Vertical format for TikTok, Instagram Stories"
            }
        },
        "background_types": {
            "color": "Solid color gradients",
            "ai": "AI-generated images (requires model download)",
            "stock": "Stock images from Unsplash"
        }
    }

@app.post("/generate", response_model=ListicleResponse)
async def generate_listicle(request: ListicleRequest):
    """Generate listicle images"""
    
    if not generate_listicle_images:
        raise HTTPException(
            status_code=500, 
            detail="Listicle generator not available. Check server setup."
        )
    
    # Validate inputs
    valid_formats = ["landscape", "portrait"]
    valid_backgrounds = ["color", "ai", "stock"]
    
    if request.format_type not in valid_formats:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid format. Must be one of: {valid_formats}"
        )
    
    if request.background_type not in valid_backgrounds:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid background type. Must be one of: {valid_backgrounds}"
        )
    
    if not request.topic.strip():
        raise HTTPException(
            status_code=400,
            detail="Topic cannot be empty"
        )
    
    if request.num_slides < 1 or request.num_slides > 10:
        raise HTTPException(
            status_code=400,
            detail="Number of slides must be between 1 and 10"
        )
    
    try:
        print(f"Generating listicle: {request.topic}, {request.format_type}, {request.background_type}")
        # Generate the listicle
        image_paths = generate_listicle_images(
            topic=request.topic,
            format_type=request.format_type,
            background_type=request.background_type,
            num_slides=request.num_slides
        )
        print(f"Generated paths: {image_paths}")
        
        # Convert paths to proper URLs
        image_urls = []
        
        for path in image_paths:
            # Handle relative paths from the generator
            if path.startswith('../outputs/'):
                # Remove the '../outputs/' prefix and use the rest
                clean_path = path.replace('../outputs/', '')
                image_url = f"/outputs/{clean_path}"
            else:
                # Handle absolute paths
                abs_outputs_dir = os.path.abspath(outputs_dir)
                abs_image_path = os.path.abspath(path)
                rel_path = os.path.relpath(abs_image_path, abs_outputs_dir)
                image_url = f"/outputs/{rel_path}"
            image_urls.append(image_url)
        
        # Create download ZIP
        download_url = create_download_zip(image_paths, request.topic, request.format_type)
        
        return ListicleResponse(
            success=True,
            message=f"Successfully generated {len(image_paths)} slides",
            images=image_urls,
            download_url=download_url
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating listicle: {str(e)}"
        )

def create_download_zip(image_paths: List[str], topic: str, format_type: str) -> str:
    """Create a ZIP file with all generated images"""
    
    # Create temp ZIP file
    temp_dir = tempfile.mkdtemp()
    zip_filename = f"{topic.replace(' ', '_').lower()}_{format_type}.zip"
    zip_path = os.path.join(temp_dir, zip_filename)
    
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for image_path in image_paths:
            if os.path.exists(image_path):
                # Add file to ZIP with just the filename
                filename = os.path.basename(image_path)
                zipf.write(image_path, filename)
    
    # Move to outputs directory for serving
    final_zip_path = os.path.join(outputs_dir, zip_filename)
    shutil.move(zip_path, final_zip_path)
    
    # Clean up temp directory
    shutil.rmtree(temp_dir)
    
    # Return relative URL
    return f"/outputs/{zip_filename}"

@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download a specific file"""
    
    file_path = os.path.join(outputs_dir, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream'
    )

@app.get("/health")
async def health_check():
    """Detailed health check"""
    
    health_status = {
        "api": "running",
        "generator_available": generate_listicle_images is not None,
        "outputs_directory": os.path.exists(outputs_dir)
    }
    
    return health_status

if __name__ == "__main__":
    import uvicorn
    
    print("Starting Faceless Video Automation API...")
    print("Visit http://localhost:8000/docs for API documentation")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )