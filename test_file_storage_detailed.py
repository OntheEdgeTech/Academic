import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config.settings import Config
from src.services.file_service import FileStorageService

def test_file_storage_detailed():
    print("Testing File Storage Service...")
    
    # Check if file storage folder exists
    print(f"File storage folder exists: {Config.FILE_STORAGE_FOLDER.exists()}")
    print(f"File storage folder: {Config.FILE_STORAGE_FOLDER}")
    
    # List a specific file
    test_file = "landing.png"
    filepath = Config.FILE_STORAGE_FOLDER / test_file
    print(f"Test file exists: {filepath.exists()}")
    
    # Check public flag file
    flag_path = Config.FILE_STORAGE_FOLDER / f"{test_file}.public"
    print(f"Public flag file exists before toggle: {flag_path.exists()}")
    
    # Toggle status
    result = FileStorageService.toggle_public_status(test_file)
    print(f"Toggle result: {result}")
    print(f"Public flag file exists after toggle: {flag_path.exists()}")
    
    # Check status
    is_public = FileStorageService.is_file_public(test_file)
    print(f"Is public after toggle: {is_public}")
    
    # Toggle back
    result = FileStorageService.toggle_public_status(test_file)
    print(f"Toggle back result: {result}")
    print(f"Public flag file exists after toggle back: {flag_path.exists()}")

if __name__ == "__main__":
    test_file_storage_detailed()