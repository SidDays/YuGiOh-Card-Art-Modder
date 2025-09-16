from PIL import Image, ImageDraw, ImageFont
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
        output_filename = f"{name}_title.png"

    # Create the final canvas
    final_img = Image.new('RGBA', (384, 48), (255, 255, 255, 0))

    # Create a temporary image for the text itself
    text_img = Image.new('RGBA', (296, 32), (255, 255, 255, 0))
    draw = ImageDraw.Draw(text_img)

    # --- Font Selection ---
    font_size = 32
    try:
        # Use a common font, fallback to default
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print(f"Font at '{font_path}' not found. Using default font.")
        font = ImageFont.load_default()
        text_width, text_height = draw.textbbox((0,0), name, font=font)[2:]
        font_size = int(32 * (32 / text_height))
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()

    # --- Text Rendering and Horizontal Squishing ---
    text_render_width = draw.textlength(name, font=font)

    if text_render_width > 296:
        # If text is too wide, squish it.
        temp_squish_img = Image.new('RGBA', (int(text_render_width), 32), (255, 255, 255, 0))
        temp_squish_draw = ImageDraw.Draw(temp_squish_img)
        temp_squish_draw.text((0, 0), name, font=font, fill="black")
        text_img = temp_squish_img.resize((296, 32), Image.Resampling.LANCZOS)
    else:
        # If the text fits, draw it directly.
        draw.text((0, 0), name, font=font, fill="black")

    # --- Paste the text image onto the final canvas ---
    final_img.paste(text_img, (32, 8))

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
