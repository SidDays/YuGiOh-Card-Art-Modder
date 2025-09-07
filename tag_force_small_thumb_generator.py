import sys
import os
from PIL import Image

def create_tiny_thumbnail(input_image_path):
    """
    Processes an input image to create a tiny thumbnail for Tag Force.

    Args:
        input_image_path (str): The path to the source image.
    """
    try:
        # Open the source image
        source_image = Image.open(input_image_path).convert("RGBA")
    except FileNotFoundError:
        print(f"Error: Input image not found at {input_image_path}")
        sys.exit(1)

    # Resize the source image to 305x305
    resized_image = source_image.resize((305, 305), Image.Resampling.LANCZOS)

    # Create a new blank 400x583 canvas
    canvas = Image.new('RGBA', (400, 583), (0, 0, 0, 0))

    # Overlay the resized image onto the canvas at position (48, 106)
    canvas.paste(resized_image, (48, 106))

    # Resize the entire canvas to 256x256
    final_image = canvas.resize((256, 256), Image.Resampling.LANCZOS)

    # Determine the output path
    base_name, extension = os.path.splitext(input_image_path)
    output_path = f"{base_name}_tiny_overlay.png"

    # Save the final image
    final_image.save(output_path)
    print(f"Successfully created tiny thumbnail: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python tag_force_small_thumb_generator.py <input_image>")
        print("Example: python tag_force_small_thumb_generator.py image_source.png")
        sys.exit(1)

    # Check if the Pillow library is installed
    try:
        from PIL import Image
    except ImportError:
        print("Pillow library not found. Please install it using: pip install Pillow")
        sys.exit(1)
        
    input_image = sys.argv[1]
    create_tiny_thumbnail(input_image)
