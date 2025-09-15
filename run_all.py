import os
import subprocess
import sys

def run_overlay_for_directory(target_directory):
    """
    Finds all .png files in the specified directory and its subdirectories,
    then runs the image_overlay.py script for each of them.
    """
    if not os.path.isdir(target_directory):
        print(f"Error: Directory not found at '{target_directory}'")
        sys.exit(1)

    print(f"Scanning for .png files in '{target_directory}'...")
    
    png_files = []
    for root, _, files in os.walk(target_directory):
        for file in files:
            if file.lower().endswith('.png'):
                full_path = os.path.join(root, file)
                png_files.append(full_path)

    if not png_files:
        print(f"No .png files found to process in '{target_directory}'.")
        return

    print(f"Found {len(png_files)} .png files to process.")

    for png_file in png_files:
        print(f"\n--- Processing {png_file} ---")
        try:
            # Use sys.executable to ensure we're using the same python interpreter
            # Pass the full path of the png file to the overlay script
            subprocess.run(
                [sys.executable, "image_overlay.py", png_file], 
                check=True
            )
            print(f"Successfully processed {png_file}")
        except subprocess.CalledProcessError as e:
            print(f"Error processing {png_file}: {e}")
        except FileNotFoundError:
            print(f"Error: 'image_overlay.py' not found. Make sure it is in the same directory as this script.")
            sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python run_all.py <directory_path>")
        print("Example: python run_all.py \"C:\\path\\to\\images\"")
        sys.exit(1)
        
    input_directory = sys.argv[1]
    run_overlay_for_directory(input_directory)
