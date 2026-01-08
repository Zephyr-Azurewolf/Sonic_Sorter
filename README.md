🎵 Sonic Sorter (Music Library Organizer) 
VERSION 4.0
Author: Zephyr-Azurewolf
Language: Python 3.x

A high-performance automated music organizer that scans audio files and sorts them into "Warm" (Analog/Organic) or "Cold" (Digital/Mechanical) directories based on there metadata.

✨ Features
Intelligent Regex Matching: Uses a custom "flexible separator" logic. It correctly identifies genres regardless of formatting (e.g., matching "Hip Hop" against Hip-Hop, Hip&Hop, or Hip/Hop).

Whole-Word Precision: Prevents substring collisions. "Pop" will match Pop but will not accidentally steal Synthpop or K-Pop.

Visual Feedback: Features a real-time progress bar with ETA and processing speed (powered by tqdm).

Format Support: Automatically handles .mp3 (ID3) and .flac (Vorbis) metadata.

Non-Destructive: Copies files to the new destination, preserving your original Master Library.

🛠️ Prerequisites
You need Python 3.6+ and the following external libraries:

mutagen: For reading audio metadata.

tqdm: For the progress bar interface.

Installation
Bash

pip install mutagen tqdm
⚙️ Configuration
1. The Genre Lists (config.py)
The sorting logic relies on a local configuration file named config.py. This file must contain two lists: warm_list and cold_list.

Python

# config.py example

warm_list = [
    "jazz", "rock", "soul", "hip hop", "acoustic"
]

cold_list = [
    "techno", "industrial", "synthpop", "vocaloid"
]
2. The Script Paths
Open music_sorter.py and update the PATHS dictionary at the top to match your file system:

Python

PATHS = {
   "SOURCE": r"C:\Path\To\My\Music",
   "WARM":   r"C:\Path\To\Output\Warm",
   "COLD":   r"C:\Path\To\Output\Cold",
   "UNDEF":  r"C:\Path\To\Output\Undefined"
}
🚀 How It Works:

The script classifies music into two philosophical categories:

🔥 Warm: Analog, harmonic, human-groove, organic (e.g., Jazz, Rock, Soul).

❄️ Cold: Digital, precise, mechanical, synthetic (e.g., Techno, Industrial, IDM).

The Regex Engine
The script pre-compiles search patterns for maximum efficiency. It uses a "Flexible Glue" technique to handle inconsistent tagging:

Normalization: It converts config entries (e.g., "R&B") into atomic words (R, B).

Flexible Matching: It injects a regex pattern [\s\-\&]+ between words.

Result: A config entry for "Hip Hop" will successfully catch file tags like Hip-Hop, Hip&Hop, or Hip - Hop.

Boundary Protection: It uses Lookarounds (?<!\w) to ensure it only matches whole words, preventing "Pop" from matching "Pope" or "Synthpop".

📂 Project Structure
Plaintext

/Sorting_Project
│
├── music_sorter.py    # Main executable script
├── config.py          # User-defined genre lists
└── README.md          # Project documentation

📝 License
This project is open-source and available for personal use and modification.
