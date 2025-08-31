import json
import os
from typing import Dict
from pathlib import Path
from flask import request, make_response
from ..config.settings import Config
from ..models.like_models import CourseLike

class LikeService:
    """Service class for managing course likes"""
    
    @staticmethod
    def _get_likes_file_path() -> Path:
        """Get the path to the likes data file"""
        return Config.DATA_FOLDER / 'likes.json'
    
    @staticmethod
    def _load_likes_data() -> Dict[str, int]:
        """Load likes data from file"""
        likes_file = LikeService._get_likes_file_path()
        if likes_file.exists():
            try:
                with open(likes_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    @staticmethod
    def _save_likes_data(likes_data: Dict[str, int]) -> bool:
        """Save likes data to file"""
        try:
            likes_file = LikeService._get_likes_file_path()
            # Create data directory if it doesn't exist
            likes_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(likes_file, 'w') as f:
                json.dump(likes_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving likes data: {e}")
            return False
    
    @staticmethod
    def get_course_likes(course_id: str) -> int:
        """Get the number of likes for a course"""
        likes_data = LikeService._load_likes_data()
        return likes_data.get(course_id, 0)
    
    @staticmethod
    def add_like(course_id: str) -> int:
        """Add a like to a course and return the new count"""
        likes_data = LikeService._load_likes_data()
        current_likes = likes_data.get(course_id, 0)
        likes_data[course_id] = current_likes + 1
        if LikeService._save_likes_data(likes_data):
            return likes_data[course_id]
        return current_likes
    
    @staticmethod
    def remove_like(course_id: str) -> int:
        """Remove a like from a course and return the new count"""
        likes_data = LikeService._load_likes_data()
        current_likes = likes_data.get(course_id, 0)
        if current_likes > 0:
            likes_data[course_id] = current_likes - 1
            if LikeService._save_likes_data(likes_data):
                return likes_data[course_id]
        return current_likes
    
    @staticmethod
    def get_all_likes() -> Dict[str, int]:
        """Get likes for all courses"""
        return LikeService._load_likes_data()
    
    @staticmethod
    def get_user_liked_courses() -> Dict[str, bool]:
        """Get courses that the current user has liked from cookies"""
        liked_courses_cookie = request.cookies.get('liked_courses', '{}')
        try:
            return json.loads(liked_courses_cookie)
        except:
            return {}
    
    @staticmethod
    def add_user_like(course_id: str) -> Dict[str, bool]:
        """Add a course to the user's liked courses in cookies"""
        liked_courses = LikeService.get_user_liked_courses()
        liked_courses[course_id] = True
        return liked_courses
    
    @staticmethod
    def remove_user_like(course_id: str) -> Dict[str, bool]:
        """Remove a course from the user's liked courses in cookies"""
        liked_courses = LikeService.get_user_liked_courses()
        if course_id in liked_courses:
            del liked_courses[course_id]
        return liked_courses
    
    @staticmethod
    def create_liked_response(response, liked_courses: Dict[str, bool]):
        """Add liked courses tracking cookie to response"""
        response.set_cookie(
            'liked_courses', 
            json.dumps(liked_courses), 
            max_age=30 * 24 * 60 * 60  # 30 days
        )
        return response