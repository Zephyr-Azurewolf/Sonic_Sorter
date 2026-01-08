"""
Music Library Sorter (Optimized Regex)
------------------------------------------------------------------------------
Author: Zephyr-Azurewolf
Description: 
    Scans a directory of audio files, extracts genre metadata, and sorts 
    files into 'Warm' or 'Cold' directories based on custom genre lists.
    
    *Optimized with pre-compiled Regex for maximum performance.*
"""

import os
import shutil
import sys
import re
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

# --- PRE-COMPILE REGEX PATTERNS ---
print("Compiling search patterns...")

def _normalize_sep(text):
    if not isinstance(text, str):
        return ''
    # replace common separators (spaces, hyphens, ampersands) with a single space and trim
    return re.sub(r'[\s\-\&]+', ' ', text).strip()

def build_flexible_pattern(genre_list):
    pattern_parts = []
    for genre in genre_list:
        # Normalize configured genre entries (e.g. "Hip-Hop" -> "Hip Hop", "R&B" -> "R B")
        clean_genre = _normalize_sep(genre)

        # Skip empty entries
        if not clean_genre:
            continue
        
        # Split into individual words
        words = clean_genre.split()
        
        # Re-join words with a flexible regex for separators
        # [\s\-\&]+ means: "Match one or more spaces, hyphens, or ampersands"
        # re.escape(w) makes sure the words themselves are safe
        flexible_regex = r'[\s\-\&]+'.join(re.escape(w) for w in words)
        
        pattern_parts.append(flexible_regex)
    
    # If no valid patterns, return a regex that never matches
    if not pattern_parts:
        return re.compile(r'(?!)')

    # Use lookaround boundaries to match whole-word sequences more robustly
    full_pattern = r'(?<!\w)(?:' + '|'.join(pattern_parts) + r')(?!\w)'
    return re.compile(full_pattern, re.IGNORECASE)

# Generate the smart patterns
WARM_PATTERN = build_flexible_pattern(config.warm_list)
COLD_PATTERN = build_flexible_pattern(config.cold_list)

def setup_directories():
    for key, path in PATHS.items():
        if key != "SOURCE":
            os.makedirs(path, exist_ok=True)

def get_genre(file_path):
    try:
        ext = file_path.lower()
        if ext.endswith('.mp3'):
            return EasyID3(file_path).get('genre', [''])[0].strip()
        elif ext.endswith('.flac'):
            return FLAC(file_path).get('genre', [''])[0].strip()
        return ""
    except Exception:
        return "no_metadata"

def sort_library():
    print("--- Starting Music Library Sort ---")
    
    if not os.path.exists(PATHS["SOURCE"]):
        print(f"Error: Source directory not found.")
        return

    setup_directories()

    # 1. Gather files
    print("Scanning for audio files...")
    all_files = []
    valid_extensions = (".mp3", ".flac", ".wav", ".m4a")
    for root, _, files in os.walk(PATHS["SOURCE"]):
        for file in files:
            if file.lower().endswith(valid_extensions):
                all_files.append(os.path.join(root, file))

    print(f"Found {len(all_files)} tracks. Beginning sort...")

    # 2. Process files
    for file_path in tqdm(all_files, desc="Processing", unit="track", colour="green", ascii=False):
        
        filename = os.path.basename(file_path)
        genre_tag = get_genre(file_path) # We don't need .lower() anymore, regex handles it
        
        destination = PATHS["UNDEF"]
        status_icon = "❓"
        status_label = "UNDEFINED"

        # 3. FAST CHECKS using pre-compiled patterns
        # We check Cold first (priority), then Warm
        if COLD_PATTERN.search(genre_tag):
            destination = PATHS["COLD"]
            status_icon = "❄️"
            status_label = "COLD"
        
        elif WARM_PATTERN.search(genre_tag):
            destination = PATHS["WARM"]
            status_icon = "🔥"
            status_label = "WARM"

        # 4. Log & Copy
        tqdm.write(f"[{status_icon} {status_label}] {filename[:30]:<30} | Genre: {genre_tag}")

        try:
            shutil.copy2(file_path, os.path.join(destination, filename))
        except Exception as e:
            tqdm.write(f"❌ Error copying {filename}: {e}")

    print("\n" + "="*40)
    print("Sorting Complete.")
    input("Press Enter to exit...")

if __name__ == "__main__":
    sort_library()
