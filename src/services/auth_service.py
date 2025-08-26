from flask import session
from ..config.settings import Config

class AuthService:
    """Service class for authentication operations"""
    
    @staticmethod
    def is_logged_in() -> bool:
        """Check if user is logged in as admin"""
        return session.get('admin_logged_in', False)
    
    @staticmethod
    def authenticate(username: str, password: str) -> bool:
        """Authenticate user credentials"""
        return (username == Config.ADMIN_USERNAME and 
                password == Config.ADMIN_PASSWORD)
    
    @staticmethod
    def login():
        """Set user as logged in"""
        session['admin_logged_in'] = True
    
    @staticmethod
    def logout():
        """Log out user"""
        session.pop('admin_logged_in', None)