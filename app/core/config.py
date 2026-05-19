# app/core/config.py (add these settings)

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Upload settings
UPLOAD_DIR = BASE_DIR / "uploads"
PROJECT_THUMBNAIL_DIR = UPLOAD_DIR / "projects" / "thumbnails"
HIERARCHY_THUMBNAIL_DIR = UPLOAD_DIR / "hierarchy" / "thumbnails"

# Ensure directories exist
PROJECT_THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)
HIERARCHY_THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)

# URL prefix for serving static files
STATIC_URL = "/static"
UPLOAD_URL = f"{STATIC_URL}/uploads"