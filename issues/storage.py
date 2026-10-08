import json
import os

from django.conf import settings

ISSUES_FILE = settings.DATABASE_DIR / "issues.json"
REPORTERS_FILE = settings.DATABASE_DIR / "reporters.json"

def read_json(path):
    """
    Return the list stored in the file.  
    A missing or empty file is an empty list.
    """
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            text = f.read().strip()
    except FileNotFoundError:
        return []
    if not text:
        return []
    return json.loads(text)

def write_json(path, data):
    """
    Write data to the file, creating the folder if needed.
    """

    # Create the parent directory
    path.parent.mkdir(parents=True, exist_ok=True)

    # Create a temperory file path
    tmp_path = path.with_suffix(".json.tmp")

    # Write json to temperory file
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    # Replace the old file with completed file
    os.replace(tmp_path, path)