# tag_force_cropper.py
import sys
import os
from PIL import Image

def transform_image(source_path, dest_path):
    """
    Resizes the source image to 320x320 if necessary, then crops three
    rectangular parts and arranges them on a new transparent canvas.
    """
    try:
        # 1. Load the source image from the provided path
        source_img = Image.open(source_path)
    except FileNotFoundError:
        print(f"Error: The source file '{source_path}' was not found.")
        return
    except Exception as e:
        print(f"An error occurred while opening the image: {e}")
        return

    # 2. Check and resize the image if it's not 312x312
    required_source_size = (312, 312)
    if source_img.size != required_source_size:
        print(f"Source image is not {required_source_size}. Resizing...")
        # Use LANCZOS for high-quality downsampling
        source_img = source_img.resize(required_source_size, Image.Resampling.LANCZOS)

    # 3. Define the crop regions for the 312x312 source image
    red_crop_box = (0, 0, 312, 240)
    yellow_crop_box = (0, 240, 192, 312)
    green_crop_box = (192, 240, 312, 312)

    # 4. Crop the parts from the (potentially resized) source image
    red_part = source_img.crop(red_crop_box)
    yellow_part = source_img.crop(yellow_crop_box)
    green_part = source_img.crop(green_crop_box)

    # 5. Create a new transparent canvas for the destination image
    dest_size = (512, 256)
    dest_img = Image.new('RGBA', dest_size, (0, 0, 0, 0))

    # 6. Define the scaled positions to paste the cropped parts
    red_paste_pos = (0, 0)
    yellow_paste_pos = (320, 0)
    green_paste_pos = (320, 80)

    # 7. Paste the parts onto the new canvas
    dest_img.paste(red_part, red_paste_pos)
    dest_img.paste(yellow_part, yellow_paste_pos)
    dest_img.paste(green_part, green_paste_pos)
    
    # 8. Convert to PNG8 before saving.
    print("Converting image to PNG8 for compression...")
    dest_img = dest_img.quantize(colors=256, dither=Image.Dither.FLOYDSTEINBERG)

    # 9. Save the final, compressed image.
    dest_img.save(dest_path)
    print(f"Transformation complete. Image saved as '{dest_path}'")

# This is the main execution block
if __name__ == "__main__":
    # sys.argv is a list containing command-line arguments.
    # sys.argv[0] is the script name.
    # sys.argv[1] is the first argument (the file path).
    if len(sys.argv) < 2:
        print("Usage: Drag and drop a PNG file onto this script.")
        print("Or run from the command line: python tag_force_cropper.py <path_to_your_image>")
        sys.exit() # Exit the script if no file is provided.

    # Get the input file path from the command-line argument
    input_path = sys.argv[1]

    # Automatically create a name for the output file
    # e.g., 'C:\\Users\\Me\\Desktop\\photo.png'
    # becomes 'C:\\Users\\Me\\Desktop\\photo_processed.png'
    path_without_ext, ext = os.path.splitext(input_path)
    output_path = f"{path_without_ext}_processed{ext}"

    # Run the main function with the provided file paths
    transform_image(source_path=input_path, dest_path=output_path)