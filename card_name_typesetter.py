from PIL import Image, ImageDraw, ImageFont
import os

def create_text_image(name, width=296, height=32, output_filename=None, font_path="Yu-Gi-Oh! Matrix Regular Small Caps 2.ttf"):
    """
    Creates a PNG image with the given text typeset onto a canvas of a specified size.

    Args:
        name (str): The text to write on the image.
        width (int): The width of the canvas.
        height (int): The height of the canvas.
        output_filename (str): The name of the output PNG file.
        font_path (str): Path to the TTF font file.
    """
    if output_filename is None:
        output_filename = f"{name}_title.png"
    # Create a transparent canvas
    img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # --- Font Selection ---
    font_size = height
    try:
        # Use a common font, fallback to default
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print(f"Font at '{font_path}' not found. Using default font.")
        # For the default font, the size parameter is not as straightforward.
        # We'll have to guess and check or use a different approach.
        # A simple approximation is to use a large point size and scale down.
        font = ImageFont.load_default()
        # With default font, we can't easily control size. This part will be less accurate.
        # Let's render and then resize the whole image to fit the height.
        # This is a fallback and might not be perfect.
        text_width, text_height = draw.textbbox((0,0), name, font=font)[2:]
        font_size = int(height * (height / text_height))
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()


    # --- Text Rendering and Horizontal Squishing ---
    # Get the width of the text if drawn normally
    text_width = draw.textlength(name, font=font)

    if text_width > width:
        # If text is too wide, we need to squish it.
        # 1. Create a temporary image with the full text width
        temp_img = Image.new('RGBA', (int(text_width), height), (255, 255, 255, 0))
        temp_draw = ImageDraw.Draw(temp_img)
        
        # 2. Draw the text on the temporary image (left-aligned)
        # The vertical position is adjusted slightly to center it better.
        temp_draw.text((0, 0), name, font=font, fill="black")
        
        # 3. Resize (squish) this temporary image to the target width
        img = temp_img.resize((width, height), Image.Resampling.LANCZOS)
    else:
        # If the text fits, draw it directly on the main image
        # The vertical position is adjusted slightly to center it better.
        draw.text((0, 0), name, font=font, fill="black")

    # --- Save the result ---
    img.save(output_filename, "PNG")
    print(f"Image saved as {output_filename}")
    return output_filename

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create an image with typeset text.")
    parser.add_argument("name", type=str, help="The text to write on the image.")
    parser.add_argument("--width", type=int, default=296, help="The width of the canvas.")
    parser.add_argument("--height", type=int, default=32, help="The height of the canvas.")
    parser.add_argument("--font", type=str, default="Yu-Gi-Oh! Matrix Regular Small Caps 2.ttf", help="Path to the TTF font file.")
    parser.add_argument("-o", "--output", dest="output_filename", type=str, default=None,
                        help="The name of the output PNG file (default: {name}_title.png)")

    args = parser.parse_args()

    create_text_image(args.name, args.width, args.height, args.output_filename, args.font)
