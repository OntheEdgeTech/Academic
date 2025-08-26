import os
from pathlib import Path

class Config:
    """Application configuration class"""
    
    # Base directories
    BASE_DIR = Path(__file__).parent.parent.parent
    COURSES_FOLDER = BASE_DIR / 'courses'
    STATIC_FOLDER = BASE_DIR / 'static'
    TEMPLATES_FOLDER = BASE_DIR / 'templates'
    FILE_STORAGE_FOLDER = BASE_DIR / 'file_storage'
    
    # File storage configuration
    ALLOWED_EXTENSIONS = {
        'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 
        'xls', 'xlsx', 'ppt', 'pptx', 'zip', 'rar', 'mp4', 'avi', 
        'mov', 'wmv', 'flv', 'mkv', 'webm', 'mp3', 'wav', 'py', 
        'js', 'html', 'css', 'java', 'cpp', 'c', 'php', 'rb', 
        'swift', 'go', 'sql', 'json', 'xml', 'yml', 'yaml', 'md', 'csv'
    }
    
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    # Default admin credentials (username: admin, password: password)
    ADMIN_USERNAME = 'admin'
    ADMIN_PASSWORD = 'password'
    
    # Cookie settings
    COOKIE_MAX_AGE = 30 * 24 * 60 * 60  # 30 days
    
    @classmethod
    def init_app(cls, app):
        """Initialize application with configuration"""
        # Configure template and static folders
        app.template_folder = str(cls.TEMPLATES_FOLDER)
        app.static_folder = str(cls.STATIC_FOLDER)
        
        # Ensure file storage directory exists
        cls.FILE_STORAGE_FOLDER.mkdir(exist_ok=True)