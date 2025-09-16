from PIL import Image, ImageDraw, ImageFont
from pathvalidate import sanitize_filename
import os

def create_text_image(name, output_filename=None, font_path="Yu-Gi-Oh! Matrix Regular Small Caps 2.ttf"):
    """
    Creates a PNG image with the given text typeset onto a canvas of a specified size.

    Args:
        name (str): The text to write on the image.
        output_filename (str): The name of the output PNG file.
        font_path (str): Path to the TTF font file.
    """
    if output_filename is None:
        sanitized_name = sanitize_filename(name)
        output_filename = f"{sanitized_name}_title.png"

    # Create the final canvas
    final_img = Image.new('RGBA', (384, 48), (255, 255, 255, 0))

    # Create a temporary image for the text itself
    text_img = Image.new('RGBA', (296, 32), (255, 255, 255, 0))
    draw = ImageDraw.Draw(text_img)

    # --- Font Selection ---
    font_size = 60
    try:
        # Use a common font, fallback to default
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print(f"Font at '{font_path}' not found. Using default font.")
        font = ImageFont.load_default()
        # Fallback font sizing is less precise
        bbox = draw.textbbox((0,0), name, font=font)
        text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
        font_size = int(32 * (32 / text_height))
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()

    # --- Text Rendering ---
    # Get the actual bounding box of the text to account for descenders
    bbox = font.getbbox(name)
    text_render_width = bbox[2]  # width
    text_render_height = bbox[3] # height, includes descenders

    # Create a correctly sized temporary image for the text
    text_img = Image.new('RGBA', (text_render_width, text_render_height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(text_img)
    draw.text((0, 0), name, font=font, fill="black")

    # --- Horizontal Squishing if necessary ---
    if text_render_width > 296:
        # If text is too wide, squish it to the target width.
        text_img = text_img.resize((296, text_render_height), Image.Resampling.LANCZOS)

    # --- Paste the text image onto the final canvas ---
    # Use the generated text image as a mask to draw directly on the final image.
    # This allows glyphs to bleed out of the conceptual text box without being clipped.
    # This position was hardcoded based on the reference image.
    final_img.paste(text_img, (16, 0), mask=text_img)

    # --- Save the result ---
    final_img.save(output_filename, "PNG")
    print(f"Image saved as {output_filename}")
    return output_filename

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create an image with typeset text.")
    parser.add_argument("name", type=str, help="The text to write on the image.")
    parser.add_argument("--font", type=str, default="Yu-Gi-Oh! Matrix Regular Small Caps 2.ttf", help="Path to the TTF font file.")
    parser.add_argument("-o", "--output", dest="output_filename", type=str, default=None,
                        help="The name of the output PNG file (default: {name}_title.png)")

    args = parser.parse_args()

    create_text_image(args.name, args.output_filename, args.font)
