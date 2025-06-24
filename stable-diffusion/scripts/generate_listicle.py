#!/usr/bin/env python3
"""
Generate listicle images for social media with flexible size and background options.
"""

import os
import requests
import glob
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from diffusers import StableDiffusionPipeline
import torch

# Format configurations
FORMATS = {
    'landscape': {
        'width': 1920,
        'height': 1080,
        'name': 'YouTube/Landscape'
    },
    'portrait': {
        'width': 1080, 
        'height': 1920,
        'name': 'TikTok/Portrait'
    }
}

# Background type options
BACKGROUND_TYPES = {
    'color': 'Solid color gradients',
    'ai': 'AI-generated images',
    'stock': 'Stock images from Unsplash'
}

def generate_listicle_images(topic, format_type='landscape', background_type='color', num_slides=5):
    """Generate listicle images with specified format and background type."""
    
    if format_type not in FORMATS:
        raise ValueError(f"Format must be one of: {list(FORMATS.keys())}")
    
    if background_type not in BACKGROUND_TYPES:
        raise ValueError(f"Background type must be one of: {list(BACKGROUND_TYPES.keys())}")
    
    format_config = FORMATS[format_type]
    width, height = format_config['width'], format_config['height']
    
    print(f"Generating {format_config['name']} listicle ({width}x{height})")
    print(f"Background type: {BACKGROUND_TYPES[background_type]}")
    
    # Generate content for the topic
    slides_content = generate_content_for_topic(topic, num_slides)
    
    # Create output directory using absolute path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_outputs_dir = os.path.join(script_dir, '..', 'outputs')
    output_dir = os.path.join(base_outputs_dir, format_type)
    os.makedirs(output_dir, exist_ok=True)
    
    # Clean up old images (optional - keeps last 10 images)
    cleanup_old_images(output_dir)
    
    generated_images = []
    
    for i, slide_data in enumerate(slides_content):
        print(f"Generating slide {i+1}/{num_slides}: {slide_data['title']}")
        
        # Generate background based on type
        if background_type == 'color':
            background = create_color_background(width, height, i)
        elif background_type == 'ai':
            background = create_ai_background(width, height, slide_data)
        elif background_type == 'stock':
            background = create_stock_background(width, height, slide_data, topic)
        else:
            background = create_color_background(width, height, i)  # fallback
        
        # Add text overlay
        image_with_text = add_text_overlay(background, slide_data, i+1, format_type)
        
        # Save image with timestamp to avoid caching issues
        import time
        timestamp = int(time.time())
        clean_topic = topic.replace(' ', '_').replace(',', '').replace(':', '').lower()
        filename = f"slide_{i+1:02d}_{clean_topic}_{format_type}_{timestamp}.png"
        filepath = os.path.join(output_dir, filename)
        image_with_text.save(filepath)
        generated_images.append(filepath)
        
        print(f"Saved: {filepath}")
    
    return generated_images

def create_color_background(width, height, slide_index):
    """Create a gradient color background."""
    
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
    
    base_color = colors[slide_index % len(colors)]
    
    # Create gradient
    image = Image.new('RGB', (width, height), base_color)
    draw = ImageDraw.Draw(image)
    
    # Create diagonal gradient
    for i in range(max(width, height)):
        factor = 1.0 - (i / max(width, height)) * 0.4
        gradient_color = tuple(int(c * factor) for c in base_color)
        
        # Draw diagonal lines for gradient effect
        if i < width:
            draw.line([(i, 0), (i, height)], fill=gradient_color)
        if i < height:
            draw.line([(0, i), (width, i)], fill=gradient_color)
    
    return image

def create_ai_background(width, height, slide_data):
    """Create AI-generated background using Stable Diffusion."""
    
    try:
        # Initialize pipeline if not already done
        if not hasattr(create_ai_background, 'pipe'):
            print("Loading Stable Diffusion model...")
            create_ai_background.pipe = StableDiffusionPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5",
                torch_dtype=torch.float16,
                use_safetensors=True
            )
            create_ai_background.pipe = create_ai_background.pipe.to("mps")
        
        # Create prompt based on slide theme
        prompt = f"minimalist gradient background, {slide_data['visual_theme']}, professional, clean design, no text, abstract"
        
        # Generate image
        image = create_ai_background.pipe(
            prompt=prompt,
            negative_prompt="text, letters, words, watermark, signature, people, faces, objects",
            height=height,
            width=width,
            guidance_scale=7.5,
            num_inference_steps=20
        ).images[0]
        
        return image
        
    except Exception as e:
        print(f"AI generation failed: {e}")
        print("Falling back to color background...")
        return create_color_background(width, height, 0)

def create_stock_background(width, height, slide_data, topic):
    """Create background using stock images from Unsplash."""
    
    try:
        # Extract keywords from topic for search
        keywords = topic.lower().replace('top ', '').replace('best ', '')
        keywords = keywords.replace('ultimate ', '').replace('essential ', '')
        
        # Search terms for abstract/professional backgrounds
        search_terms = [
            f"{keywords} abstract",
            f"{keywords} professional",
            "gradient abstract",
            "minimal professional",
            "business background"
        ]
        
        # Try each search term
        for search_term in search_terms:
            try:
                # Use Unsplash API (no key needed for basic usage)
                url = f"https://source.unsplash.com/{width}x{height}/?{search_term.replace(' ', ',')}"
                
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    # Save temp image
                    temp_path = f"../temp/stock_bg_{hash(search_term)}.jpg"
                    os.makedirs("../temp", exist_ok=True)
                    
                    with open(temp_path, 'wb') as f:
                        f.write(response.content)
                    
                    # Load and process image
                    image = Image.open(temp_path)
                    image = image.convert('RGB')
                    
                    # Apply dark overlay for text readability
                    overlay = Image.new('RGBA', image.size, (0, 0, 0, 100))
                    image = Image.alpha_composite(image.convert('RGBA'), overlay)
                    
                    # Clean up temp file
                    os.remove(temp_path)
                    
                    return image.convert('RGB')
                    
            except Exception as e:
                print(f"Stock image search failed for '{search_term}': {e}")
                continue
        
        # If all searches fail, use color background
        print("All stock image searches failed, using color background")
        return create_color_background(width, height, 0)
        
    except Exception as e:
        print(f"Stock background creation failed: {e}")
        return create_color_background(width, height, 0)

def generate_content_for_topic(topic, num_slides):
    """Generate actual content based on the topic."""
    
    # Extract the main subject from topic
    clean_topic = topic.lower()
    for prefix in ["top ", "best ", "ultimate ", "essential "]:
        if clean_topic.startswith(prefix):
            clean_topic = clean_topic.replace(prefix, "", 1)
            break
    
    import re
    clean_topic = re.sub(r'^\d+\s*', '', clean_topic)
    
    # Content database for different topics
    content_library = {
        # Productivity
        "productivity": [
            {"title": "Time Blocking", "subtitle": "Schedule your day in focused chunks"},
            {"title": "The 2-Minute Rule", "subtitle": "If it takes less than 2 minutes, do it now"},
            {"title": "Eliminate Distractions", "subtitle": "Turn off notifications during deep work"},
            {"title": "Batch Similar Tasks", "subtitle": "Group emails, calls, and admin together"},
            {"title": "Take Regular Breaks", "subtitle": "Use the Pomodoro Technique for focus"},
        ],
        "marketing": [
            {"title": "Know Your Audience", "subtitle": "Create detailed buyer personas"},
            {"title": "Content is King", "subtitle": "Provide value before asking for anything"},
            {"title": "Social Proof Works", "subtitle": "Show testimonials and reviews"},
            {"title": "Test Everything", "subtitle": "A/B test your headlines and calls-to-action"},
            {"title": "Follow Up Consistently", "subtitle": "Most sales happen after 5+ touchpoints"},
        ],
        "fitness": [
            {"title": "Start Small", "subtitle": "Begin with 15-minute daily workouts"},
            {"title": "Consistency Beats Intensity", "subtitle": "Regular exercise is better than sporadic"},
            {"title": "Track Your Progress", "subtitle": "Use apps or journals to monitor gains"},
            {"title": "Mix Cardio & Strength", "subtitle": "Combine both for optimal health"},
            {"title": "Rest is Essential", "subtitle": "Recovery days prevent injury and burnout"},
        ],
        "money": [
            {"title": "Emergency Fund First", "subtitle": "Save 3-6 months of expenses"},
            {"title": "Automate Your Savings", "subtitle": "Set up automatic transfers to savings"},
            {"title": "Invest Early & Often", "subtitle": "Time in market beats timing the market"},
            {"title": "Track Your Spending", "subtitle": "Know where every dollar goes"},
            {"title": "Increase Your Income", "subtitle": "Focus on skills that pay more"},
        ],
        "travel": [
            {"title": "Book Flights Early", "subtitle": "Save money with advance booking"},
            {"title": "Pack Light", "subtitle": "One carry-on makes everything easier"},
            {"title": "Research Local Culture", "subtitle": "Respect customs and traditions"},
            {"title": "Keep Copies of Documents", "subtitle": "Store digital and physical backups"},
            {"title": "Stay Connected", "subtitle": "Get local SIM or international plan"},
        ],
        "health": [
            {"title": "Drink More Water", "subtitle": "Aim for 8 glasses daily"},
            {"title": "Prioritize Sleep", "subtitle": "7-9 hours for optimal health"},
            {"title": "Eat Whole Foods", "subtitle": "Choose minimally processed options"},
            {"title": "Move Every Hour", "subtitle": "Combat sedentary lifestyle"},
            {"title": "Manage Stress", "subtitle": "Practice meditation or deep breathing"},
        ],
        "cooking": [
            {"title": "Prep Ingredients First", "subtitle": "Mise en place makes cooking smoother"},
            {"title": "Season at Every Step", "subtitle": "Build layers of flavor"},
            {"title": "Sharp Knives Are Safer", "subtitle": "Keep your knives properly maintained"},
            {"title": "Taste as You Cook", "subtitle": "Adjust seasoning throughout"},
            {"title": "Keep It Simple", "subtitle": "Master basics before complex dishes"},
        ],
        "learning": [
            {"title": "Active Recall", "subtitle": "Test yourself instead of re-reading"},
            {"title": "Spaced Repetition", "subtitle": "Review material at increasing intervals"},
            {"title": "Teach Others", "subtitle": "Explaining concepts reinforces knowledge"},
            {"title": "Practice Deliberately", "subtitle": "Focus on weaknesses, not strengths"},
            {"title": "Take Breaks", "subtitle": "Let your brain process and consolidate"},
        ],
    }
    
    # Find matching content based on keywords
    topic_keywords = clean_topic.split()
    matched_content = None
    
    for key, content in content_library.items():
        if any(keyword in key for keyword in topic_keywords) or any(keyword in clean_topic for keyword in [key]):
            matched_content = content
            break
    
    # If no match found, generate generic advice
    if not matched_content:
        matched_content = [
            {"title": "Research First", "subtitle": f"Learn the fundamentals of {clean_topic}"},
            {"title": "Start Small", "subtitle": f"Begin with simple {clean_topic} practices"},
            {"title": "Be Consistent", "subtitle": f"Regular practice improves {clean_topic} skills"},
            {"title": "Learn from Others", "subtitle": f"Find mentors in {clean_topic}"},
            {"title": "Measure Progress", "subtitle": f"Track your {clean_topic} improvements"},
            {"title": "Stay Updated", "subtitle": f"Keep learning new {clean_topic} trends"},
            {"title": "Practice Daily", "subtitle": f"Make {clean_topic} part of your routine"},
            {"title": "Get Feedback", "subtitle": f"Ask for input on your {clean_topic} approach"},
        ]
    
    # Visual themes for different backgrounds
    themes = [
        "modern blue professional",
        "vibrant energetic orange", 
        "calm trustworthy green",
        "elegant sophisticated purple",
        "warm inviting gold",
        "cool contemporary teal",
        "bold confident red",
        "sleek minimal gray"
    ]
    
    # Select content for the number of slides requested
    slides = []
    for i in range(num_slides):
        content_item = matched_content[i % len(matched_content)]
        slides.append({
            "title": content_item["title"],
            "subtitle": content_item["subtitle"],
            "visual_theme": themes[i % len(themes)]
        })
    
    return slides

def add_text_overlay(image, slide_data, slide_number, format_type):
    """Add text overlay optimized for the specified format with better text wrapping."""
    
    img_with_text = image.copy()
    draw = ImageDraw.Draw(img_with_text)
    
    width, height = img_with_text.size
    
    # Adjust font sizes and margins based on format
    if format_type == 'portrait':
        title_size = 75
        subtitle_size = 45
        number_size = 100
        margin = 60
        text_margin = 100  # Side margins for text
    else:
        title_size = 70
        subtitle_size = 42
        number_size = 90
        margin = 80
        text_margin = 150  # Side margins for text
    
    # Try to load system fonts with bold weight
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", title_size)
        subtitle_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", subtitle_size)
        number_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", number_size)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        number_font = ImageFont.load_default()
    
    # Add semi-transparent overlay for better text readability
    overlay = Image.new('RGBA', image.size, (0, 0, 0, 100))
    img_with_text = Image.alpha_composite(img_with_text.convert('RGBA'), overlay)
    draw = ImageDraw.Draw(img_with_text)
    
    # Add slide number (top left)
    number_text = f"{slide_number}"
    draw.text((margin, margin), number_text, font=number_font, fill="white", 
              stroke_width=3, stroke_fill="black")
    
    # Wrap title text if too long
    max_title_width = width - (text_margin * 2)
    wrapped_title = wrap_text(slide_data['title'], title_font, max_title_width, draw)
    
    # Calculate title position (centered)
    title_lines = wrapped_title.split('\n')
    title_line_height = title_size + 10
    total_title_height = len(title_lines) * title_line_height
    title_start_y = (height // 2) - (total_title_height // 2) - 30
    
    # Draw title lines
    for i, line in enumerate(title_lines):
        line_bbox = draw.textbbox((0, 0), line, font=title_font)
        line_width = line_bbox[2] - line_bbox[0]
        line_x = (width - line_width) // 2
        line_y = title_start_y + (i * title_line_height)
        
        draw.text((line_x, line_y), line, font=title_font, fill="white", 
                  stroke_width=4, stroke_fill="black")
    
    # Wrap subtitle text if too long
    max_subtitle_width = width - (text_margin * 2)
    wrapped_subtitle = wrap_text(slide_data['subtitle'], subtitle_font, max_subtitle_width, draw)
    
    # Calculate subtitle position (below title)
    subtitle_lines = wrapped_subtitle.split('\n')
    subtitle_line_height = subtitle_size + 8
    subtitle_start_y = title_start_y + total_title_height + 50
    
    # Draw subtitle lines
    for i, line in enumerate(subtitle_lines):
        line_bbox = draw.textbbox((0, 0), line, font=subtitle_font)
        line_width = line_bbox[2] - line_bbox[0]
        line_x = (width - line_width) // 2
        line_y = subtitle_start_y + (i * subtitle_line_height)
        
        draw.text((line_x, line_y), line, font=subtitle_font, fill="white",
                  stroke_width=2, stroke_fill="black")
    
    return img_with_text.convert('RGB')

def wrap_text(text, font, max_width, draw):
    """Wrap text to fit within max_width."""
    words = text.split(' ')
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        bbox = draw.textbbox((0, 0), test_line, font=font)
        text_width = bbox[2] - bbox[0]
        
        if text_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
                current_line = word
            else:
                # Word is too long, force it
                lines.append(word)
    
    if current_line:
        lines.append(current_line)
    
    return '\n'.join(lines)

def cleanup_old_images(output_dir, keep_latest=10):
    """Clean up old generated images, keeping only the most recent ones."""
    try:
        # Get all PNG files in the directory
        image_files = glob.glob(os.path.join(output_dir, "*.png"))
        
        if len(image_files) <= keep_latest:
            return
        
        # Sort by modification time (newest first)
        image_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
        # Remove older files
        files_to_remove = image_files[keep_latest:]
        for file_path in files_to_remove:
            try:
                os.remove(file_path)
                print(f"Cleaned up old image: {os.path.basename(file_path)}")
            except OSError as e:
                print(f"Error removing {file_path}: {e}")
                
    except Exception as e:
        print(f"Error during cleanup: {e}")

if __name__ == "__main__":
    import sys
    
    print("Listicle Generator")
    print("=================")
    
    # Get topic
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        topic = input("Enter your listicle topic: ").strip()
        if not topic:
            topic = "Top 5 Productivity Tips"
    
    # Get format
    print(f"\nAvailable formats:")
    for key, config in FORMATS.items():
        print(f"  {key}: {config['name']} ({config['width']}x{config['height']})")
    
    format_choice = input("\nChoose format (landscape/portrait): ").strip().lower()
    if format_choice not in FORMATS:
        format_choice = 'landscape'
    
    # Get background type
    print(f"\nAvailable background types:")
    for key, desc in BACKGROUND_TYPES.items():
        print(f"  {key}: {desc}")
    
    bg_choice = input("\nChoose background type (color/ai/stock): ").strip().lower()
    if bg_choice not in BACKGROUND_TYPES:
        bg_choice = 'color'
    
    print(f"\nGenerating listicle for: {topic}")
    print(f"Format: {FORMATS[format_choice]['name']}")
    print(f"Background: {BACKGROUND_TYPES[bg_choice]}")
    
    try:
        images = generate_listicle_images(topic, format_choice, bg_choice)
        print(f"\nGenerated {len(images)} listicle slides:")
        for img in images:
            print(f"  - {img}")
        print("\nListicle generation complete!")
        
    except Exception as e:
        print(f"Error generating listicle: {e}")
        import traceback
        traceback.print_exc()