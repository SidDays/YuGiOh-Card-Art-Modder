import sys
import os
import numpy as np
from PIL import Image

def calculate_mse(imageA, imageB):
    """Calculates the Mean Squared Error between two images."""
    # Convert images to numpy arrays
    arrA = np.array(imageA)
    arrB = np.array(imageB)
    
    # The 'Mean Squared Error' between the two images is the
    # sum of the squared difference between the two images;
    # NOTE: the two images must have the same dimension
    err = np.sum((arrA.astype("float") - arrB.astype("float")) ** 2)
    err /= float(arrA.shape[0] * arrA.shape[1])
    
    # return the MSE, the lower the error, the more "similar"
    # the two images are
    return err

def find_best_match(image_id):
    """
    Finds the best match for a small image within a directory of atlas images.

    Args:
        image_id (str): The ID of the image to find.
    """
    # --- 1. Load and Prepare the Source Image ---
    small_image_path = os.path.join("small", f"{image_id}.png")
    try:
        source_image = Image.open(small_image_path).convert("RGBA")
    except FileNotFoundError:
        print(f"Error: Source image not found at '{small_image_path}'")
        sys.exit(1)

    # Resize the source image to the target dimensions for comparison
    needle_image = source_image.resize((88, 120), Image.Resampling.LANCZOS)
    print(f"Loaded and resized '{small_image_path}' to 88x120 for matching.")

    # --- 2. Define Atlas Parameters ---
    tiny_dir = "tiny"
    if not os.path.isdir(tiny_dir):
        print(f"Error: Directory '{tiny_dir}/' not found.")
        sys.exit(1)

    sub_image_width = 88
    sub_image_height = 120
    cols = 23
    rows = 17

    best_match = {
        "file": None,
        "x_index": -1,
        "y_index": -1,
        "mse": float('inf')
    }

    # --- 3. Crawl Through Atlases and Find the Best Match ---
    print(f"Searching for best match in atlases in '{tiny_dir}/'...")
    atlas_files = [f for f in os.listdir(tiny_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]

    if not atlas_files:
        print(f"No image atlases found in '{tiny_dir}/'.")
        sys.exit(1)

    for atlas_filename in atlas_files:
        atlas_path = os.path.join(tiny_dir, atlas_filename)
        print(f"  - Processing atlas: {atlas_filename}")
        atlas_image = Image.open(atlas_path).convert("RGBA")

        for r in range(rows):
            for c in range(cols):
                # Define the box for the sub-image
                left = c * sub_image_width
                top = r * sub_image_height
                right = left + sub_image_width
                bottom = top + sub_image_height
                
                # Crop the sub-image from the atlas
                haystack_image = atlas_image.crop((left, top, right, bottom))
                
                # Compare with the needle
                mse = calculate_mse(needle_image, haystack_image)
                
                # If it's a better match, update our records
                if mse < best_match["mse"]:
                    best_match["mse"] = mse
                    best_match["file"] = atlas_filename
                    best_match["x_index"] = c
                    best_match["y_index"] = r
                    # If we find a perfect match, we can stop early
                    if mse == 0:
                        break
            if mse == 0:
                break
        if mse == 0:
            break
            
    # --- 4. Return the Result ---
    if best_match["file"]:
        pixel_x = best_match['x_index'] * sub_image_width
        pixel_y = best_match['y_index'] * sub_image_height
        print("\n--- Match Found! ---")
        print(f"Atlas File: {best_match['file']}")
        print(f"Best Match Pixel X: {pixel_x}")
        print(f"Best Match Pixel Y: {pixel_y}")
        print(f"Confidence (MSE): {best_match['mse']:.2f} (lower is better)")
    else:
        print("\nCould not find a suitable match in any atlas.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python tag_force_tiny_thumb_finder.py <image_id>")
        print("Example: python tag_force_tiny_thumb_finder.py 4007")
        sys.exit(1)

    # Check for dependencies
    try:
        from PIL import Image
        import numpy
    except ImportError:
        print("Error: Missing dependencies. Please install Pillow and NumPy:")
        print("pip install Pillow numpy")
        sys.exit(1)

    image_id_arg = sys.argv[1]
    find_best_match(image_id_arg)
