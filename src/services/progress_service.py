import json
from typing import Dict, Any
from flask import request, make_response
from ..config.settings import Config

class UserProgressService:
    """Service class for user progress tracking"""
    
    @staticmethod
    def get_user_progress(course_id: str) -> Dict[str, bool]:
        """Get user's progress for a specific course from cookies"""
        progress_key = f"course_progress_{course_id}"
        progress_data = request.cookies.get(progress_key, "{}")
        try:
            return json.loads(progress_data)
        except:
            return {}
    
    @staticmethod
    def add_document_to_progress(course_id: str, doc_filename: str) -> Dict[str, bool]:
        """Add a document to user's progress for a course"""
        progress = UserProgressService.get_user_progress(course_id)
        if doc_filename not in progress:
            progress[doc_filename] = True
        return progress
    
    @staticmethod
    def create_progress_response(response, course_id: str, progress: Dict[str, bool]):
        """Add progress tracking cookie to response"""
        progress_key = f"course_progress_{course_id}"
        response.set_cookie(
            progress_key, 
            json.dumps(progress), 
            max_age=Config.COOKIE_MAX_AGE
        )
        return response