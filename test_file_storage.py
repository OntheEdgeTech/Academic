import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config.settings import Config
from src.services.file_service import FileStorageService

def test_file_storage():
    print("Testing File Storage Service...")
    
    # Check if file storage folder exists
    print(f"File storage folder exists: {Config.FILE_STORAGE_FOLDER.exists()}")
    print(f"File storage folder: {Config.FILE_STORAGE_FOLDER}")
    
    # List current files
    files = FileStorageService.get_all_files()
    print(f"Current files: {len(files)}")
    for file in files:
        print(f"  - {file['filename']} ({file['size']} bytes, public: {file['is_public']})")
    
    # Test public status toggle
    if files:
        filename = files[0]['filename']
        print(f"\nTesting public status toggle for: {filename}")
        
        # Check current status
        is_public = FileStorageService.is_file_public(filename)
        print(f"Current public status: {is_public}")
        
        # Toggle status
        result = FileStorageService.toggle_public_status(filename)
        print(f"Toggle result: {result}")
        
        # Check new status
        is_public = FileStorageService.is_file_public(filename)
        print(f"New public status: {is_public}")
        
        # Toggle back
        result = FileStorageService.toggle_public_status(filename)
        print(f"Toggle back result: {result}")

if __name__ == "__main__":
    test_file_storage()