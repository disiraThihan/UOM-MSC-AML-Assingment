"""
Create a clean, submission-ready ZIP file for the Moodle submission page.
Excludes virtual environments, cache files, and unnecessary temp files.
"""

import os
import zipfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ZIP_OUTPUT = os.path.join(BASE_DIR, "Colombo_Land_Valuation_AI_MSc_Submission.zip")

INCLUDE_FILES = [
    "Written_Report_Machine_Learning_Assignment.pdf",
    "ASSIGNMENT_REPORT.md",
    "README.md",
    "VIDEO_WALKTHROUGH_SCRIPT.md",
    "Colombo_Land_Valuation_System_Presentation.pptx",
    "Colombo_Land_Valuation_AI_Presentation.pptx",
    "requirements.txt",
    "run_server.sh",
    "generate_pdf_report.py",
    "generate_presentation.py"
]

INCLUDE_DIRS = [
    "src",
    "data",
    "models",
    "templates",
    "static"
]

EXCLUDE_EXTS = [".pyc", ".DS_Store", ".log"]
EXCLUDE_DIRS = [".venv", "__pycache__", ".git", "catboost_info"]

def package():
    print(f"Creating submission zip: {ZIP_OUTPUT} ...")
    with zipfile.ZipFile(ZIP_OUTPUT, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add root files
        for fname in INCLUDE_FILES:
            fpath = os.path.join(BASE_DIR, fname)
            if os.path.exists(fpath):
                zipf.write(fpath, arcname=os.path.join("colombo_land_valuation_ai", fname))
                print(f"  Added file: {fname}")

        # Add directories
        for dname in INCLUDE_DIRS:
            dirpath = os.path.join(BASE_DIR, dname)
            if os.path.exists(dirpath):
                for root, dirs, files in os.walk(dirpath):
                    # Filter out excluded dirs in-place
                    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
                    for f in files:
                        if any(f.endswith(ext) for ext in EXCLUDE_EXTS):
                            continue
                        full_path = os.path.join(root, f)
                        rel_path = os.path.relpath(full_path, BASE_DIR)
                        arc_name = os.path.join("colombo_land_valuation_ai", rel_path)
                        zipf.write(full_path, arcname=arc_name)
                print(f"  Added directory: {dname}/")

    size_mb = os.path.getsize(ZIP_OUTPUT) / (1024 * 1024)
    print(f"\nSuccessfully generated submission ZIP: {ZIP_OUTPUT} ({size_mb:.2f} MB)")

if __name__ == "__main__":
    package()
