"""
Music Library Sorter
------------------------------------------------------------------------------
Author: Zephyr_Azurewolf
Description: 
    Scans a directory of audio files (.mp3, .flac, .wav, .m4a), extracts genre 
    metadata, and sorts the files into 'Warm' or 'Cold' directories based on 
    custom genre lists defined in config.py.

    Utilizes 'tqdm' for a visual progress bar and 'mutagen' for metadata parsing.
    Uses Regex word boundaries to prevent substring collisions (e.g. 'Pop' vs 'Synthpop').

Dependencies:
    pip install mutagen tqdm
"""

import os
import shutil
import sys
import re  # Added for Regex matching
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
from tqdm import tqdm
import config  # Local import: config.py must contain warm_list and cold_list

# --- CONFIGURATION ---
# usage: Replace these paths with your actual directories before running.
PATHS = {
   "SOURCE": r"path/to/your/source_library",
    "WARM":   r"path/to/your/output/warm_music",
    "COLD":   r"path/to/your/output/cold_music",
    "UNDEF":  r"path/to/your/output/undefined"
}

def setup_directories():
    """Ensures that all destination directories exist."""
    for key, path in PATHS.items():
        if key != "SOURCE":  # Don't create the source, obviously
            os.makedirs(path, exist_ok=True)

def get_genre(file_path):
    """
    Extracts the genre from audio metadata.
    Supports MP3 (EasyID3) and FLAC.
    """
    try:
        ext = file_path.lower()
        if ext.endswith('.mp3'):
            # EasyID3 returns a list; we take the first item
            return EasyID3(file_path).get('genre', [''])[0].lower().strip()
        elif ext.endswith('.flac'):
            return FLAC(file_path).get('genre', [''])[0].lower().strip()
        return ""
    except Exception:
        return "no_metadata"

def collect_audio_files(source_dir):
    """Recursively finds all valid audio files in the source directory."""
    audio_files = []
    valid_extensions = (".mp3", ".flac", ".wav", ".m4a")
    
    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.lower().endswith(valid_extensions):
                audio_files.append(os.path.join(root, file))
    return audio_files

def is_whole_word_match(genre_list, tag):
    """
    Checks if any item in the list matches the tag as a WHOLE word.
    Example: 'pop' will match 'indie pop' but NOT 'synthpop'.
    """
    if not tag: return False
    
    for item in genre_list:
        # \b ensures we match word boundaries (start/end of string or space)
        # re.escape ensures special characters in genres (like R&B) are treated literally
        pattern = r'\b' + re.escape(item) + r'\b'
        if re.search(pattern, tag):
            return True
    return False

def sort_library():
    """Main execution function."""
    print("--- Starting Music Library Sort ---")
    
    if not os.path.exists(PATHS["SOURCE"]):
        print(f"Error: Source directory not found at {PATHS['SOURCE']}")
        return

    setup_directories()

    # 1. Gather files
    print("Scanning for audio files...")
    all_files = collect_audio_files(PATHS["SOURCE"])
    print(f"Found {len(all_files)} tracks. Beginning sort...")

    # 2. Process files with Progress Bar
    # ascii=False allows for smooth block characters if terminal supports it
    for file_path in tqdm(all_files, desc="Processing", unit="track", colour="green", ascii=False):
        
        filename = os.path.basename(file_path)
        genre_tag = get_genre(file_path)
        
        # Determine Destination
        destination = PATHS["UNDEF"]
        status_icon = "❓"  # Default icon
        status_label = "UNDEFINED"

        # Check Cold List 
        if is_whole_word_match(config.cold_list, genre_tag):
            destination = PATHS["COLD"]
            status_icon = "❄️"
            status_label = "COLD"
            
        # Check Warm List
        elif is_whole_word_match(config.warm_list, genre_tag):
            destination = PATHS["WARM"]
            status_icon = "🔥"
            status_label = "WARM"

        # 3. Logging (using tqdm.write to avoid breaking the progress bar)
        # Format: [ICON] Filename (truncated) | Genre
        log_message = f"[{status_icon} {status_label}] {filename[:30]:<30} | Genre: {genre_tag}"
        tqdm.write(log_message)

        # 4. Copy File
        try:
            target_path = os.path.join(destination, filename)
            shutil.copy2(file_path, target_path)
        except Exception as e:
            tqdm.write(f"❌ Error copying {filename}: {e}")

    print("\n" + "="*40)
    print("Sorting Complete.")
    print("="*40)

    input("Press Enter to exit...")


if __name__ == "__main__":
    sort_library()