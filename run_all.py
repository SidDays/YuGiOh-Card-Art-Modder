import os
import subprocess
import sys

def run_overlay_for_all_pngs():
    """
    Finds all .png files in the current directory
    and runs the image_overlay.py script for each of them.
    """
    # List of files/directories to exclude from processing
    excluded_items = [
        'image_overlay.py',
        'tag_force_cropper.py',
        'tag_force_small_thumb_generator.py',
        'tag_force_tiny_thumb_finder.py',
        'run_all.py',  # Exclude the script itself
        'large',
        'small',
        'tiny',
        'output',
        'backup',
        '__pycache__'
    ]

    # Get the current directory
    current_directory = os.getcwd()
    
    # Find all .png files in the current directory
    png_files = []
    for item in os.listdir(current_directory):
        if item.lower().endswith('.png') and item not in excluded_items:
            png_files.append(item)

    if not png_files:
        print("No .png files found to process in the current directory")
        return

    print(f"Found {len(png_files)} .png files to process.")

    for png_file in png_files:
        print(f"\n--- Processing {png_file} ---")
        try:
            # Use sys.executable to ensure we're using the same python interpreter
            subprocess.run(
                [sys.executable, "image_overlay.py", png_file], 
                check=True
            )
            print(f"Successfully processed {png_file}")
        except subprocess.CalledProcessError as e:
            print(f"Error processing {png_file}: {e}")
        except FileNotFoundError:
            print(f"Error: 'image_overlay.py' not found. Make sure you are in the correct directory.")
            sys.exit(1)

if __name__ == "__main__":
    run_overlay_for_all_pngs()
