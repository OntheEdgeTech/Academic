import os
import json
from typing import List, Dict
from pathlib import Path
from ..utils.helpers import allowed_file, generate_unique_filename, sanitize_path
from ..config.settings import Config

class FileStorageService:
    """Service class for file storage operations"""
    
    @staticmethod
    def get_all_files() -> List[Dict]:
        """Get list of all files in file storage"""
        files = []
        if Config.FILE_STORAGE_FOLDER.exists():
            for file_path in Config.FILE_STORAGE_FOLDER.iterdir():
                if file_path.is_file() and not file_path.name.endswith('.public'):
                    stat = file_path.stat()
                    files.append({
                        'filename': file_path.name,
                        'size': stat.st_size,
                        'modified': stat.st_mtime,
                        'is_public': (Config.FILE_STORAGE_FOLDER / f"{file_path.name}.public").exists()
                    })
        
        return sorted(files, key=lambda x: x['modified'], reverse=True)
    
    @staticmethod
    def upload_files(uploaded_files) -> tuple[int, int]:
        """Upload multiple files and return (success_count, error_count)"""
        success_count = 0
        error_count = 0
        
        if not uploaded_files or all(f.filename == '' for f in uploaded_files):
            return success_count, error_count
        
        for file in uploaded_files:
            if file and file.filename and allowed_file(file.filename):
                filename = file.filename
                # Check if file already exists
                filepath = Config.FILE_STORAGE_FOLDER / filename
                if filepath.exists():
                    filename = generate_unique_filename(filename)
                    filepath = Config.FILE_STORAGE_FOLDER / filename
                
                try:
                    file.save(str(filepath))
                    success_count += 1
                except Exception as e:
                    print(f"Error saving file {filename}: {e}")
                    error_count += 1
            else:
                error_count += 1
        
        return success_count, error_count
    
    @staticmethod
    def delete_file(filename: str) -> bool:
        """Delete a file from storage"""
        if not sanitize_path(filename):
            return False
            
        filepath = Config.FILE_STORAGE_FOLDER / filename
        if filepath.exists():
            try:
                filepath.unlink()
                # Also remove public flag file if exists
                flag_path = Config.FILE_STORAGE_FOLDER / f"{filename}.public"
                if flag_path.exists():
                    flag_path.unlink()
                return True
            except Exception as e:
                print(f"Error deleting file: {e}")
                return False
        return False
    
    @staticmethod
    def toggle_public_status(filename: str) -> bool:
        """Toggle public status of a file"""
        if not sanitize_path(filename):
            return False
            
        filepath = Config.FILE_STORAGE_FOLDER / filename
        if filepath.exists():
            flag_path = Config.FILE_STORAGE_FOLDER / f"{filename}.public"
            try:
                if flag_path.exists():
                    flag_path.unlink()  # Make private
                else:
                    flag_path.touch()   # Make public
                return True
            except Exception as e:
                print(f"Error toggling public status: {e}")
                return False
        return False
    
    @staticmethod
    def is_file_public(filename: str) -> bool:
        """Check if a file is marked as public"""
        if not sanitize_path(filename):
            return False
            
        public_flag = Config.FILE_STORAGE_FOLDER / f"{filename}.public"
        return public_flag.exists()