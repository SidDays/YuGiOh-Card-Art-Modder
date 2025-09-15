from PIL import Image, ImageDraw, ImageFont
import os

def create_text_image(text, width, height, output_filename="text_image.png"):
    """
    Creates a PNG image with the given text typeset onto a canvas of a specified size.

    Args:
        text (str): The text to write on the image.
        width (int): The width of the canvas.
        height (int): The height of the canvas.
        output_filename (str): The name of the output PNG file.
    """
    # Create a transparent canvas
    img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # --- Font Selection ---
    font_size = height
    try:
        # Use a common font, fallback to default
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        print("Arial font not found. Using default font.")
        # For the default font, the size parameter is not as straightforward.
        # We'll have to guess and check or use a different approach.
        # A simple approximation is to use a large point size and scale down.
        font = ImageFont.load_default()
        # With default font, we can't easily control size. This part will be less accurate.
        # Let's render and then resize the whole image to fit the height.
        # This is a fallback and might not be perfect.
        text_width, text_height = draw.textbbox((0,0), text, font=font)[2:]
        font_size = int(height * (height / text_height))
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()


    # --- Text Rendering and Horizontal Squishing ---
    # Get the width of the text if drawn normally
    text_width = draw.textlength(text, font=font)

    if text_width > width:
        # If text is too wide, we need to squish it.
        # 1. Create a temporary image with the full text width
        temp_img = Image.new('RGBA', (int(text_width), height), (255, 255, 255, 0))
        temp_draw = ImageDraw.Draw(temp_img)
        
        # 2. Draw the text on the temporary image (left-aligned)
        # The vertical position is adjusted slightly to center it better.
        temp_draw.text((0, 0), text, font=font, fill="black")
        
        # 3. Resize (squish) this temporary image to the target width
        img = temp_img.resize((width, height), Image.Resampling.LANCZOS)
    else:
        # If the text fits, draw it directly on the main image
        # The vertical position is adjusted slightly to center it better.
        draw.text((0, 0), text, font=font, fill="black")

    # --- Save the result ---
    img.save(output_filename, "PNG")
    print(f"Image saved as {output_filename}")
    return output_filename

# --- Example Usage ---
text_to_render = "Hello world"
canvas_width = 296
canvas_height = 32
output_file = create_text_image(text_to_render, canvas_width, canvas_height)

# Display the image if in a Jupyter-like environment
try:
    from IPython.display import display, Image as IPImage
    display(IPImage(filename=output_file))
except ImportError:
    print("Could not display image. Please open the file manually.")

# --- Example with longer text that will be squished ---
long_text = "This is a much longer string of text that will certainly not fit in the original width."
squished_output_file = create_text_image(long_text, canvas_width, canvas_height, "squished_text_image.png")

try:
    from IPython.display import display, Image as IPImage
    display(IPImage(filename=squished_output_file))
except ImportError:
    print("Could not display image. Please open the file manually.")