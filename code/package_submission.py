"""
Submission Packaging Script for University of Moratuwa MSc in AI
Module: Machine Learning Assignment

Packages the reorganized folder structure:
  - code/
  - docs/
  - video/
into a clean, submission-ready ZIP strictly under the 50 MB Moodle upload limit.
"""

import os
import zipfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ZIP_OUTPUT = os.path.join(BASE_DIR, "Colombo_Land_Valuation_AI_MSc_Submission.zip")

# Primary submission folders to include
FOLDERS = ["code", "docs", "video"]

# Directories and files to exclude from submission zip
EXCLUDE_DIRS = {
    ".venv", "__pycache__", ".git", "catboost_info", "untitled folder"
}
EXCLUDE_EXTS = {
    ".pyc", ".DS_Store", ".log", ".tmp", ".bak"
}

def package():
    print(f"Creating submission zip: {ZIP_OUTPUT} ...")
    
    # Track file count and uncompressed size
    total_uncompressed = 0
    file_count = 0

    with zipfile.ZipFile(ZIP_OUTPUT, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for folder in FOLDERS:
            folder_path = os.path.join(BASE_DIR, folder)
            if not os.path.exists(folder_path):
                print(f"  [WARNING] Folder not found: {folder}")
                continue

            for root, dirs, files in os.walk(folder_path):
                # Filter out excluded directories in-place
                dirs[:] = [
                    d for d in dirs 
                    if d not in EXCLUDE_DIRS and not d.startswith('.')
                    # Exclude duplicate github-pages build inside code/
                    and not (folder == "code" and d == "docs")
                ]
                
                for f in sorted(files):
                    if f.startswith('.') or any(f.endswith(ext) for ext in EXCLUDE_EXTS):
                        continue
                    
                    full_path = os.path.join(root, f)
                    rel_path = os.path.relpath(full_path, BASE_DIR)
                    zipf.write(full_path, arcname=rel_path)
                    
                    f_size = os.path.getsize(full_path)
                    total_uncompressed += f_size
                    file_count += 1
                    print(f"  Added: {rel_path} ({f_size / (1024*1024):.2f} MB)")

    size_bytes = os.path.getsize(ZIP_OUTPUT)
    size_mb = size_bytes / (1024 * 1024)
    print("\n" + "="*60)
    print(f"Submission Package Created Successfully: {os.path.basename(ZIP_OUTPUT)}")
    print(f"  Total Files Included:  {file_count}")
    print(f"  Uncompressed Size:     {total_uncompressed / (1024*1024):.2f} MB")
    print(f"  Compressed ZIP Size:   {size_mb:.2f} MB ({size_bytes:,} bytes)")
    print(f"  Status:                {'[OK] UNDER 50 MB LIMIT' if size_mb < 50 else '[WARNING] EXCEEDS 50 MB'}")
    print("="*60)

if __name__ == "__main__":
    package()
