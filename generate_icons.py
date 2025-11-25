#!/usr/bin/env python3
"""
Generate app icons for Buzzer PWA in various sizes.
Requires: pip install Pillow
"""

from PIL import Image, ImageDraw, ImageFont
import os
import sys

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Create icons directory if it doesn't exist
icons_dir = "frontend/static/icons"
os.makedirs(icons_dir, exist_ok=True)

# Icon sizes needed
SIZES = [72, 96, 128, 144, 152, 192, 384, 512]

# Colors
PRIMARY_COLOR = "#007AFF"  # iOS blue
BACKGROUND_COLOR = "#007AFF"
TEXT_COLOR = "#FFFFFF"

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def create_icon(size):
    """Create a single icon of the given size."""

    # Create a new image with the primary color background
    img = Image.new('RGBA', (size, size), hex_to_rgb(BACKGROUND_COLOR) + (255,))
    draw = ImageDraw.Draw(img)

    # Create a circle in the center with an even lighter background
    circle_radius = size // 2 - size // 16
    circle_pos = [
        size // 2 - circle_radius,
        size // 2 - circle_radius,
        size // 2 + circle_radius,
        size // 2 + circle_radius,
    ]

    # Draw outer circle (slightly lighter shade)
    lighter_color = hex_to_rgb("#1E90FF") + (255,)
    draw.ellipse(circle_pos, fill=lighter_color)

    # Add text "B" for Buzzer in the center
    try:
        # Try to use a system font, fall back to default if not available
        font_size = int(size * 0.5)
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        # If arial.ttf not available, try other common fonts
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(size * 0.5))
        except:
            # Fall back to default font
            font = ImageFont.load_default()

    # Draw the "B" text
    text = "B"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    text_position = (
        (size - text_width) // 2,
        (size - text_height) // 2 - size // 20
    )

    draw.text(text_position, text, fill=hex_to_rgb(TEXT_COLOR) + (255,), font=font)

    return img

def main():
    """Generate all icon sizes."""
    print("Generating Buzzer app icons...")

    for size in SIZES:
        icon = create_icon(size)
        filename = f"{icons_dir}/icon-{size}x{size}.png"
        icon.save(filename, "PNG")
        print(f"✓ Generated {filename}")

    print("\n✅ All icons generated successfully!")
    print(f"\nIcons created in: {icons_dir}/")
    print("Icons are ready for deployment.")

if __name__ == "__main__":
    main()
