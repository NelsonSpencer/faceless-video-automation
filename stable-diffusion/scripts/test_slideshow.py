#!/usr/bin/env python3
"""
Test slideshow generation with placeholder images (no SD model download needed).
"""

import os
from PIL import Image, ImageDraw, ImageFont
import random

def generate_test_slideshow(topic, num_slides=5):
    """Generate test slideshow with colored backgrounds instead of AI images."""
    
    # Generate content for the topic
    slides_content = generate_content_for_topic(topic, num_slides)
    
    # Create output directory
    output_dir = "../outputs"
    os.makedirs(output_dir, exist_ok=True)
    
    generated_images = []
    
    # Color palette for backgrounds
    colors = [
        (52, 73, 94),    # Dark blue
        (231, 76, 60),   # Red
        (46, 125, 50),   # Green
        (142, 36, 170),  # Purple
        (255, 152, 0),   # Orange
        (0, 121, 107),   # Teal
        (63, 81, 181),   # Indigo
        (255, 193, 7)    # Amber
    ]
    
    for i, slide_data in enumerate(slides_content):
        print(f"Generating slide {i+1}/{num_slides}: {slide_data['title']}")
        
        # Create colored background instead of AI image
        color = colors[i % len(colors)]
        image = Image.new('RGB', (1920, 1080), color)
        
        # Add gradient effect
        image = add_gradient_effect(image, color)
        
        # Add text overlay
        image_with_text = add_text_overlay(image, slide_data, i+1)
        
        # Save image
        filename = f"slide_{i+1:02d}_{topic.replace(' ', '_').lower()}.png"
        filepath = os.path.join(output_dir, filename)
        image_with_text.save(filepath)
        generated_images.append(filepath)
        
        print(f"Saved: {filepath}")
    
    return generated_images

def add_gradient_effect(image, base_color):
    """Add a subtle gradient effect to the background."""
    width, height = image.size
    
    # Create gradient overlay
    gradient = Image.new('RGB', (width, height), base_color)
    draw = ImageDraw.Draw(gradient)
    
    # Create vertical gradient
    for y in range(height):
        # Darken towards bottom
        factor = 1.0 - (y / height) * 0.3
        darkened_color = tuple(int(c * factor) for c in base_color)
        draw.line([(0, y), (width, y)], fill=darkened_color)
    
    return gradient

def generate_content_for_topic(topic, num_slides):
    """Generate content structure for slideshow slides based on any topic."""
    
    # Extract the main subject from topic
    clean_topic = topic.lower()
    for prefix in ["top ", "best ", "ultimate ", "essential "]:
        if clean_topic.startswith(prefix):
            clean_topic = clean_topic.replace(prefix, "", 1)
            break
    
    # Remove numbers like "5", "10" etc.
    import re
    clean_topic = re.sub(r'^\d+\s*', '', clean_topic)
    
    slides = []
    for i in range(num_slides):
        slides.append({
            "title": f"Point {i+1}",
            "subtitle": f"Key insight about {clean_topic}",
            "visual_theme": f"gradient theme {i+1}"
        })
    
    return slides

def add_text_overlay(image, slide_data, slide_number):
    """Add text overlay to background image."""
    
    img_with_text = image.copy()
    draw = ImageDraw.Draw(img_with_text)
    
    width, height = img_with_text.size
    
    # Try to load system font, fall back to default
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
    import sys
    
    # Get topic from command line or prompt
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        topic = input("Enter your slideshow topic: ").strip()
        if not topic:
            topic = "Top 5 Marketing Tips"
    
    print(f"Generating test slideshow for: {topic}")
    
    try:
        images = generate_test_slideshow(topic)
        print(f"\nGenerated {len(images)} slides:")
        for img in images:
            print(f"  - {img}")
        print("\nTest slideshow generation complete!")
        
    except Exception as e:
        print(f"Error generating slideshow: {e}")
        import traceback
        traceback.print_exc()