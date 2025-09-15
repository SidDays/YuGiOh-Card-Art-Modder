import sys
import os
import subprocess
import shutil
import csv
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
    small_overlay_path = f"{base_name}_small_overlay.png"

    base_image_path = os.path.join("large", f"{image_id}.png")
    output_dir_large = os.path.join("output", "large")
    output_path_large = os.path.join(output_dir_large, f"{image_id}.png")
    backup_dir_large = os.path.join("backup", "large")
    backup_path_large = os.path.join(backup_dir_large, f"{image_id}.png")

    small_base_image_path = os.path.join("small", f"{image_id}.png")
    output_dir_small = os.path.join("output", "small")
    output_path_small = os.path.join(output_dir_small, f"{image_id}.png")
    backup_dir_small = os.path.join("backup", "small")
    backup_path_small = os.path.join(backup_dir_small, f"{image_id}.png")

    # Ensure the output and backup directories exist
    os.makedirs(output_dir_large, exist_ok=True)
    os.makedirs(backup_dir_large, exist_ok=True)
    os.makedirs(output_dir_small, exist_ok=True)
    os.makedirs(backup_dir_small, exist_ok=True)

    # Backup the original large file
    if os.path.exists(base_image_path):
        print(f"Backing up {base_image_path} to {backup_path_large}")
        shutil.copyfile(base_image_path, backup_path_large)
    else:
        print(f"Warning: {base_image_path} not found, skipping backup.")

    # Backup the original small file
    if os.path.exists(small_base_image_path):
        print(f"Backing up {small_base_image_path} to {backup_path_small}")
        shutil.copyfile(small_base_image_path, backup_path_small)
    else:
        print(f"Warning: {small_base_image_path} not found, skipping backup.")

    # Step 1: Invoke tag_force_cropper.py
    print(f"Running tag_force_cropper.py on {input_image_path}...")
    try:
        subprocess.run(["python", "tag_force_cropper.py", input_image_path], check=True)
        print(f"Successfully created {processed_image_path}")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error running tag_force_cropper.py: {e}")
        sys.exit(1)

    # Step 2: Load the large images
    try:
        base_image = Image.open(base_image_path).convert("RGBA")
        overlay_image = Image.open(processed_image_path).convert("RGBA")
        print("Large images loaded successfully.")
    except FileNotFoundError as e:
        print(f"Error loading large images: {e}")
        sys.exit(1)

    # Step 3: Overlay the large images
    base_image.paste(overlay_image, (0, 0), overlay_image)
    print("Large image overlay complete.")

    # Step 4: Save the large result
    base_image.save(output_path_large)
    print(f"Output image saved to {output_path_large}")

    # Step 5: Remove the intermediate large processed image
    try:
        os.remove(processed_image_path)
        print(f"Removed intermediate file: {processed_image_path}")
    except OSError as e:
        print(f"Error removing intermediate file: {e}")

    # --- small Image Processing ---

    # Step 6: Invoke tag_force_small_thumb_generator.py
    print(f"Running tag_force_small_thumb_generator.py on {input_image_path}...")
    try:
        subprocess.run(["python", "tag_force_small_thumb_generator.py", input_image_path], check=True)
        print(f"Successfully created {small_overlay_path}")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error running tag_force_small_thumb_generator.py: {e}")
        sys.exit(1)

    # Step 7: Load the small images
    try:
        small_base_image = Image.open(small_base_image_path).convert("RGBA")
        small_overlay_image = Image.open(small_overlay_path).convert("RGBA")
        print("small images loaded successfully.")
    except FileNotFoundError as e:
        print(f"Error loading small images: {e}")
        sys.exit(1)

    # Step 8: Overlay the small images
    small_base_image.paste(small_overlay_image, (0, 0), small_overlay_image)
    print("small image overlay complete.")

    # Step 9: Save the small result
    small_base_image.save(output_path_small)
    print(f"Output small image saved to {output_path_small}")

    # Step 10: Remove the intermediate small processed image
    try:
        os.remove(small_overlay_path)
        print(f"Removed intermediate file: {small_overlay_path}")
    except OSError as e:
        print(f"Error removing intermediate file: {e}")

    # --- Tiny Atlas Processing ---

    # Step 11: Find the small image in the tiny atlas
    print(f"Finding '{image_id}' in tiny atlases...")
    try:
        result = subprocess.run(
            ["python", "tag_force_tiny_thumb_finder.py", image_id],
            check=True,
            capture_output=True,
            text=True
        )
        
        # Parse the output from the finder script
        lines = result.stdout.strip().split('\n')
        atlas_file = None
        pixel_x, pixel_y = -1, -1

        for line in lines:
            if "Atlas File:" in line:
                atlas_file = line.split("Atlas File:")[1].strip()
            elif "Best Match Pixel X:" in line:
                pixel_x = int(line.split("Best Match Pixel X:")[1].strip())
            elif "Best Match Pixel Y:" in line:
                pixel_y = int(line.split("Best Match Pixel Y:")[1].strip())

        if not atlas_file or pixel_x == -1 or pixel_y == -1:
            print("Error: Could not parse output from tag_force_tiny_thumb_finder.py")
            sys.exit(1)
            
        print(f"Found match in '{atlas_file}' at coordinates ({pixel_x}, {pixel_y})")

    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error running tag_force_tiny_thumb_finder.py: {e}")
        if hasattr(e, 'stderr'):
            print(e.stderr)
        sys.exit(1)

    # Step 12: Backup, overlay, and save the tiny atlas
    try:
        # Define atlas paths
        atlas_path = os.path.join("tiny", atlas_file)
        backup_atlas_path = os.path.join("backup", "tiny", atlas_file)
        output_atlas_path = os.path.join("output", "tiny", atlas_file)

        # Ensure directories exist
        os.makedirs(os.path.join("backup", "tiny"), exist_ok=True)
        os.makedirs(os.path.join("output", "tiny"), exist_ok=True)

        # Backup the original atlas if it doesn't exist
        if not os.path.exists(backup_atlas_path):
            print(f"Backing up {atlas_path} to {backup_atlas_path}")
            shutil.copyfile(atlas_path, backup_atlas_path)
        else:
            print(f"Backup for {atlas_file} already exists, skipping backup.")

        # Load the modified small image and resize it for the atlas
        modified_small_image = Image.open(output_path_small).convert("RGBA")
        atlas_overlay = modified_small_image.resize((88, 120), Image.Resampling.LANCZOS)

        # Load the atlas for modification
        # If an output atlas already exists, use it; otherwise, use the original.
        if os.path.exists(output_atlas_path):
            print(f"Found existing output atlas. Loading {output_atlas_path} for modification.")
            atlas_base_image = Image.open(output_atlas_path).convert("RGBA")
        else:
            print(f"No existing output atlas found. Loading {atlas_path} for modification.")
            atlas_base_image = Image.open(atlas_path).convert("RGBA")

        # Paste the overlay
        atlas_base_image.paste(atlas_overlay, (pixel_x, pixel_y), atlas_overlay)
        
        # Save the modified atlas
        atlas_base_image.save(output_atlas_path)
        print(f"Saved modified atlas to {output_atlas_path}")

    except FileNotFoundError as e:
        print(f"Error processing atlas file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred during atlas processing: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) not in [2, 3]:
        print("Usage: python image_overlay.py <input_image> [image_id]")
        print("Example: python image_overlay.py image_source.png 4007")
        print("Example: python image_overlay.py \"Exiled Force.png\"")
        sys.exit(1)

    input_image = sys.argv[1]
    image_id = None

    if len(sys.argv) == 3:
        image_id = sys.argv[2]
    else:
        # Get the filename from the path, then remove the extension
        image_name_without_ext = os.path.splitext(os.path.basename(input_image))[0]
        try:
            with open('cards.csv', mode='r', newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if row and row[0] == image_name_without_ext:
                        image_id = row[1]
                        print(f"Found image ID {image_id} for '{image_name_without_ext}' in cards.csv")
                        break
        except FileNotFoundError:
            print("Error: cards.csv not found. Please provide an image_id.")
            sys.exit(1)
        
        if not image_id:
            print(f"Error: Image ID for '{image_name_without_ext}' not found in cards.csv. Please specify the ID manually.")
            sys.exit(1)

    # Check if the Pillow library is installed
    try:
        from PIL import Image
    except ImportError:
        print("Pillow library not found. Please install it using: pip install Pillow")
        sys.exit(1)

    overlay_images(input_image, image_id)
