import os
import json
import uuid
import re
from typing import Dict, Any, List
from werkzeug.utils import secure_filename
from pathlib import Path
from ..config.settings import Config

def format_title(text: str) -> str:
    """Format text as a title by replacing underscores/hyphens with spaces and capitalizing words"""
    if not text:
        return ""
    formatted = text.replace('_', ' ').replace('-', ' ')
    return ' '.join(word.capitalize() for word in formatted.split())

def extract_title_from_markdown(content: str, filename: str) -> str:
    """Extract title from markdown content or format filename"""
    lines = content.split('\n')
    if lines and lines[0].startswith('#'):
        return lines[0].lstrip('# ').strip()
    else:
        # Remove .md extension and format
        name_without_ext = os.path.splitext(filename)[0]
        return format_title(name_without_ext)

def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def generate_unique_filename(filename: str) -> str:
    """Generate a unique filename to prevent conflicts"""
    name, ext = os.path.splitext(filename)
    unique_name = f'{name}_{uuid.uuid4().hex[:8]}{ext}'
    return unique_name

def sanitize_path(path_segment: str) -> bool:
    """Check if path segment is safe (no directory traversal)"""
    return '..' not in path_segment and not path_segment.startswith('/')
