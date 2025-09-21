from PIL import Image
import sys
import os

# Define file names
if len(sys.argv) != 2:
    print("Usage: python uncropper.py <source_image_path>")
    sys.exit(1)

source_filename = sys.argv[1]
base_name, extension = os.path.splitext(source_filename)
output_filename = f"{base_name}_uncropped{extension}"

try:
    # 1. Load the source image
    source_image = Image.open(source_filename)
except FileNotFoundError:
    print(f"Error: Source file not found at '{source_filename}'")
    print("Please make sure the script is in the same directory as the image.")
    sys.exit(1)

# Get the source image dimensions
source_width, source_height = source_image.size

# Original dimensions the script was based on
original_width = 512
original_height = 256

# Calculate scaling factors
x_scale = source_width / original_width
y_scale = source_height / original_height

# 2. Define the crop boxes (left, top, right, bottom)
# These are inferred from image_source.png and the reference diagram
# box = (left, top, left + width, top + height)

# Red: (0, 0) with size 312x240
crop_red = (0, 0, round(312 * x_scale), round(240 * y_scale))

# Yellow: (320, 0) with size 192x72
# (Inferred to be below the red block)
crop_yellow = (round(320 * x_scale), 0, round((320 + 192) * x_scale), round(72 * y_scale))

# Green: (320, 90) with size 120x72
# (Inferred to be below red, to the right of yellow)
crop_green = (round(320 * x_scale), round(80 * y_scale), round((320 + 120) * x_scale), round((80 + 72) * y_scale))

# 3. Crop the pieces from the source image
red_piece = source_image.crop(crop_red)
yellow_piece = source_image.crop(crop_yellow)
green_piece = source_image.crop(crop_green)

# 4. Define the new image (destination)
# Size is 312x312, based on the reference diagram
canvas_width = round(312 * x_scale)
canvas_height = round(312 * y_scale)
final_image = Image.new('RGBA', (canvas_width, canvas_height), (0, 0, 0, 0)) # Transparent background

# 5. Define the paste coordinates (top-left corner)
paste_red = (0, 0)
paste_yellow = (0, round(240 * y_scale))
paste_green = (round(192 * x_scale), round(240 * y_scale))

# 6. Paste the pieces onto the new image
final_image.paste(red_piece, paste_red)
final_image.paste(yellow_piece, paste_yellow)
final_image.paste(green_piece, paste_green)

# 7. Save the final image
final_image.save(output_filename)

print(f"Successfully created '{output_filename}'")