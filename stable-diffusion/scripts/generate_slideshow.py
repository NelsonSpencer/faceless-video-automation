#!/usr/bin/env python3
"""
Generate slideshow images with text overlays for faceless content creation.
"""

import os
from PIL import Image, ImageDraw, ImageFont
from diffusers import StableDiffusionPipeline
import torch

def generate_slideshow_images(topic, num_slides=5):
    """Generate slideshow images for a given topic."""
    
    # Initialize Stable Diffusion pipeline
    pipe = StableDiffusionPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        torch_dtype=torch.float16,
        use_safetensors=True
    )
    pipe = pipe.to("mps")  # Use Metal Performance Shaders on M2 Mac
    
    # Generate content for the topic
    slides_content = generate_content_for_topic(topic, num_slides)
    
    # Create output directory
    output_dir = "../outputs"
    os.makedirs(output_dir, exist_ok=True)
    
    generated_images = []
    
    for i, slide_data in enumerate(slides_content):
        print(f"Generating slide {i+1}/{num_slides}: {slide_data['title']}")
        
        # Create background image prompt
        prompt = f"minimalist gradient background, professional, {slide_data['visual_theme']}, clean design, no text"
        
        # Generate background image
        image = pipe(
            prompt=prompt,
            negative_prompt="text, letters, words, watermark, signature, ugly, low quality",
            height=1080,
            width=1920,
            guidance_scale=7.5,
            num_inference_steps=20
        ).images[0]
        
        # Add text overlay
        image_with_text = add_text_overlay(image, slide_data, i+1)
        
        # Save image
        filename = f"slide_{i+1:02d}_{topic.replace(' ', '_').lower()}.png"
        filepath = os.path.join(output_dir, filename)
        image_with_text.save(filepath)
        generated_images.append(filepath)
        
        print(f"Saved: {filepath}")
    
    return generated_images

def generate_content_for_topic(topic, num_slides):
    """Generate content structure for slideshow slides based on any topic."""
    
    # Extract the main subject from topic (remove "top X" or "best" prefixes)
    clean_topic = topic.lower()
    for prefix in ["top ", "best ", "ultimate ", "essential "]:
        if clean_topic.startswith(prefix):
            clean_topic = clean_topic.replace(prefix, "", 1)
            break
    
    # Remove numbers like "5", "10" etc.
    import re
    clean_topic = re.sub(r'^\d+\s*', '', clean_topic)
    
    # Generate generic slides that work for any topic
    gradient_themes = [
        "professional blue gradient",
        "energetic orange gradient", 
        "trustworthy green gradient",
        "elegant purple gradient",
        "modern teal gradient",
        "vibrant red gradient",
        "sophisticated navy gradient",
        "warm golden gradient"
    ]
    
    slides = []
    for i in range(num_slides):
        slides.append({
            "title": f"Point {i+1}",
            "subtitle": f"Important aspect of {clean_topic}",
            "visual_theme": gradient_themes[i % len(gradient_themes)]
        })
    
    return slides

def add_text_overlay(image, slide_data, slide_number):
    """Add text overlay to background image."""
    
    # Create a copy to modify
    img_with_text = image.copy()
    draw = ImageDraw.Draw(img_with_text)
    
    # Image dimensions
    width, height = img_with_text.size
    
    # Try to load custom font, fall back to default
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 80)
        subtitle_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 50)
        number_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 120)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        number_font = ImageFont.load_default()
    
    # Add slide number (top left)
    number_text = f"{slide_number}"
    draw.text((80, 80), number_text, font=number_font, fill="white", stroke_width=3, stroke_fill="black")
    
    # Add title (center)
    title_bbox = draw.textbbox((0, 0), slide_data['title'], font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (width - title_width) // 2
    title_y = (height // 2) - 60
    
    draw.text((title_x, title_y), slide_data['title'], font=title_font, fill="white", 
              stroke_width=4, stroke_fill="black")
    
    # Add subtitle (below title)
    subtitle_bbox = draw.textbbox((0, 0), slide_data['subtitle'], font=subtitle_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    subtitle_x = (width - subtitle_width) // 2
    subtitle_y = title_y + 100
    
    draw.text((subtitle_x, subtitle_y), slide_data['subtitle'], font=subtitle_font, fill="white",
              stroke_width=2, stroke_fill="black")
    
    return img_with_text

if __name__ == "__main__":
    topic = "Top 5 Marketing Tips"
    print(f"Generating slideshow for: {topic}")
    
    try:
        images = generate_slideshow_images(topic)
        print(f"\nGenerated {len(images)} slides:")
        for img in images:
            print(f"  - {img}")
        print("\nSlideshow generation complete!")
        
    except Exception as e:
        print(f"Error generating slideshow: {e}")
        import traceback
        traceback.print_exc()