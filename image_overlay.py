import sys
import os
import subprocess
import shutil
from PIL import Image

def overlay_images(input_image_path, image_id):
    """
    Processes an input image, overlays it onto a base image, and saves the result.

    Args:
        input_image_path (str): The path to the source image.
        image_id (str): The ID of the image, used to find the base image.
    """
    # Define file paths
    base_name, extension = os.path.splitext(input_image_path)
    processed_image_path = f"{base_name}_processed.png"
    base_image_path = os.path.join("large", f"{image_id}.png")
    output_dir = os.path.join("output", "large")
    output_path = os.path.join(output_dir, f"{image_id}.png")
    backup_dir = os.path.join("backup", "large")
    backup_path = os.path.join(backup_dir, f"{image_id}.png")

    # Ensure the output and backup directories exist
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(backup_dir, exist_ok=True)

    # Backup the original file
    if os.path.exists(base_image_path):
        print(f"Backing up {base_image_path} to {backup_path}")
        shutil.copyfile(base_image_path, backup_path)
    else:
        print(f"Warning: {base_image_path} not found, skipping backup.")

    # Step 1: Invoke tag_force_cropper.py
    print(f"Running tag_force_cropper.py on {input_image_path}...")
    try:
        subprocess.run(["python", "tag_force_cropper.py", input_image_path], check=True)
        print(f"Successfully created {processed_image_path}")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error running tag_force_cropper.py: {e}")
        sys.exit(1)

    # Step 2: Load the images
    try:
        base_image = Image.open(base_image_path).convert("RGBA")
        overlay_image = Image.open(processed_image_path).convert("RGBA")
        print("Images loaded successfully.")
    except FileNotFoundError as e:
        print(f"Error loading images: {e}")
        sys.exit(1)

    # Step 3: Overlay the images
    # The paste method respects the alpha channel of the overlay image.
    base_image.paste(overlay_image, (0, 0), overlay_image)
    print("Image overlay complete.")

    # Step 4: Save the result
    base_image.save(output_path)
    print(f"Output image saved to {output_path}")

    # Step 5: Remove the intermediate processed image
    try:
        os.remove(processed_image_path)
        print(f"Removed intermediate file: {processed_image_path}")
    except OSError as e:
        print(f"Error removing intermediate file: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python image_overlay.py <input_image> <image_id>")
        print("Example: python image_overlay.py image_source.png 4007")
        sys.exit(1)

    input_image = sys.argv[1]
    image_id = sys.argv[2]
    
    # Check if the Pillow library is installed
    try:
        from PIL import Image
    except ImportError:
        print("Pillow library not found. Please install it using: pip install Pillow")
        sys.exit(1)

    overlay_images(input_image, image_id)
