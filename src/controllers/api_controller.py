from flask import Blueprint, jsonify
from ..services.course_service import CourseService
from ..services.progress_service import UserProgressService

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/user-progress')
def api_user_progress():
    """API endpoint to get user's progress for all courses"""
    courses = CourseService.get_all_courses()
    progress_data = {}
    
    for course in courses:
        user_progress = UserProgressService.get_user_progress(course.id)
        completed_docs = len(user_progress)
        progress_data[course.id] = {
            'completed': completed_docs,
            'total': course.docs_count,
            'percentage': int((completed_docs / course.docs_count * 100)) if course.docs_count > 0 else 0
        }
    
    return jsonify(progress_data)