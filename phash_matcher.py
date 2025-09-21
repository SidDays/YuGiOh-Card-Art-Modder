import imagehash
import os
import pickle
import time
from PIL import Image

# --- Configuration ---
# 1. Path to your texture dump with PPSSPP hashes (Set A)
set_a_folder = r"D:\tiny\dump"

# 2. Path to your correctly named textures (Set B)
set_b_folder = r"D:\tiny"

# 3. Filename for the hash database cache
cache_filename = "hash_database.cache"

# 4. Path where you want the final textures.ini to be saved
output_ini_file = r"D:\tiny\output2"

# ---------------------


def build_hash_database(folder_path, cache_file_name):
    """
    Scans the set of correctly named textures and creates a database
    of {image_hash: "clean_filename.png"}.
    --- Uses a cache file if available. ---
    """
    print(f"--- Phase 1: Building/Loading hash database from {folder_path} ---")
    
    cache_file_path = os.path.join(folder_path, cache_file_name)
    
    # --- Caching Logic ---
    if os.path.exists(cache_file_path):
        try:
            print(f"  Found cache file! Loading from {cache_file_path}...")
            with open(cache_file_path, 'rb') as f:
                database = pickle.load(f)
            print(f"--- Database load complete. Indexed {len(database)} images from cache. ---")
            return database
        except Exception as e:
            print(f"  Warning: Could not load cache file. Rebuilding. Error: {e}")

    # --- If cache not found or failed, build it ---
    print("  No valid cache found. Building database from images...")
    database = {}
    count = 0
    for filename in os.listdir(folder_path):
        if filename.endswith(".png"):
            try:
                img_path = os.path.join(folder_path, filename)
                
                # --- Use the new cropping/hashing function ---
                with Image.open(img_path) as img:
                    img_hash = imagehash.dhash(img)
                
                database[img_hash] = filename
                count += 1
                if count % 500 == 0:
                    print(f"  ...indexed {count} images.")
            except Exception as e:
                print(f"  Warning: Could not process {filename}. Error: {e}")
    
    # --- Save to cache ---
    try:
        print(f"  Saving database to cache file: {cache_file_path}")
        with open(cache_file_path, 'wb') as f:
            pickle.dump(database, f)
    except Exception as e:
        print(f"  Warning: Could not save cache file. Error: {e}")

    print(f"--- Database build complete. Indexed {count} images. ---")
    return database


def match_and_generate_ini(set_a_path, set_b_path, database, output_path):
    """
    Scans Set A (English dump), compares with the database,
    and writes the textures.ini file.
    Finds the absolute closest match instead of using a threshold.
    """
    print(f"--- Phase 2: Matching hashes from {set_a_path} ---")

    # --- Create a temp directory for comparison images ---
    output_dir = os.path.dirname(output_path)
    temp_dir = os.path.join(output_dir, "temp")
    os.makedirs(temp_dir, exist_ok=True)
    # ---------------------------------------------------------
    
    ini_entries = set()
    total_files = 0
    matches_found = 0
    
    for filename_a in os.listdir(set_a_path):
        if not filename_a.endswith(".png"):
            continue
            
        total_files += 1
        try:
            img_a_path = os.path.join(set_a_path, filename_a)
            
            # Use the new hashing function
            with Image.open(img_a_path) as img:
                hash_a = imagehash.dhash(img)
            
            # Find the closest match in the database
            best_match_filename = None
            min_distance = float('inf')

            for hash_c, filename_c in database.items():
                distance = hash_a - hash_c
                if distance < min_distance:
                    min_distance = distance
                    best_match_filename = filename_c
                # If we find a perfect match, we can stop searching for this image
                if min_distance == 0:
                    break
            # ----------------------------------------------------

            # If we found a match...
            if best_match_filename:
                # Get the PPSSPP hash (the original filename without .png)
                ppsspp_hash = os.path.splitext(filename_a)[0]
                
                # This is the line for the .ini file
                ini_line = f"{ppsspp_hash} = {best_match_filename}"
                ini_entries.add(ini_line)
                matches_found += 1

                # --- Create and save the combined image for verification ---
                try:
                    img_c_path = os.path.join(set_b_path, best_match_filename)
                    with Image.open(img_a_path) as img_a, Image.open(img_c_path) as img_c:
                        # Ensure both images are in a compatible mode, e.g., RGBA
                        img_a = img_a.convert("RGBA")
                        img_c = img_c.convert("RGBA")

                        # Create a new image to hold both, stacked vertically
                        total_height = img_a.height + img_c.height
                        max_width = max(img_a.width, img_c.width)
                        
                        combined_img = Image.new('RGBA', (max_width, total_height))
                        combined_img.paste(img_a, (0, 0))
                        combined_img.paste(img_c, (0, img_a.height))

                        # Save the combined image with distance in the filename
                        combined_filename = f"{ppsspp_hash}_{os.path.splitext(best_match_filename)[0]}_d{min_distance}.png"
                        combined_save_path = os.path.join(temp_dir, combined_filename)
                        combined_img.save(combined_save_path)

                except Exception as e:
                    print(f"  Warning: Could not create combined image for {filename_a}. Error: {e}")
                # --------------------------------------------------------------------

            if total_files % 500 == 0:
                print(f"  ...scanned {total_files} files. Found {matches_found} matches.")
                
        except Exception as e:
            print(f"  Warning: Could not process {filename_a}. Error: {e}")

    print(f"--- Matching complete. ---")
    print(f"  Total files in Set A scanned: {total_files}")
    print(f"  Total unique matches found:   {len(ini_entries)}")

    # Write the final textures.ini file
    try:
        with open(output_path, "w") as f:
            f.write("[hashes]\n")
            sorted_entries = sorted(list(ini_entries))
            for line in sorted_entries:
                f.write(line + "\n")
        print(f"\n*** SUCCESS! ***")
        print(f"Generated {output_path} with {len(ini_entries)} entries.")
    except Exception as e:
        print(f"\n*** ERROR! ***")
        print(f"Could not write to {output_path}. Error: {e}")


# --- Run the script ---
start_time = time.time()
try:
    # Phase 1 - Pass crop_box and cache_filename
    hash_db = build_hash_database(set_b_folder, cache_filename)
    
    # Phase 2 - Pass crop_box
    if hash_db:
        match_and_generate_ini(set_a_folder, set_b_folder, hash_db, output_ini_file)
    else:
        print("Error: Hash database is empty. Check Set B folder path.")

except FileNotFoundError as e:
    print(f"\n*** FATAL ERROR ***")
    print(f"Could not find folder: {e.filename}")
    print("Please check your folder paths in the configuration.")
    
end_time = time.time()
print(f"Total time taken: {end_time - start_time:.2f} seconds.")
