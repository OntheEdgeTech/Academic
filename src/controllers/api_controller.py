from flask import Blueprint, jsonify, request, make_response
from ..services.course_service import CourseService
from ..services.progress_service import UserProgressService
from ..services.like_service import LikeService

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/user-progress')
def api_user_progress():
    """API endpoint to get user's progress for all courses"""
    courses = CourseService.get_all_courses()
    progress_data = {}
    
    for course in courses:
        user_progress = UserProgressService.get_user_progress(course.id)
        completed_docs = len(user_progress)
        # Ensure percentage doesn't exceed 100
        percentage = 0
        if course.docs_count > 0:
            percentage = min(100, int((completed_docs / course.docs_count * 100)))
        
        progress_data[course.id] = {
            'completed': completed_docs,
            'total': course.docs_count,
            'percentage': percentage
        }
    
    return jsonify(progress_data)

@api_bp.route('/courses/<course_id>/like', methods=['POST'])
def like_course(course_id):
    """API endpoint to like a course"""
    try:
        # Add like to global count
        new_count = LikeService.add_like(course_id)
        
        # Add to user's liked courses
        liked_courses = LikeService.add_user_like(course_id)
        
        # Create response with cookie
        response = make_response(jsonify({
            'success': True,
            'likes': new_count
        }))
        
        response = LikeService.create_liked_response(response, liked_courses)
        return response
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/courses/<course_id>/unlike', methods=['POST'])
def unlike_course(course_id):
    """API endpoint to unlike a course"""
    try:
        # Remove like from global count
        new_count = LikeService.remove_like(course_id)
        
        # Remove from user's liked courses
        liked_courses = LikeService.remove_user_like(course_id)
        
        # Create response with cookie
        response = make_response(jsonify({
            'success': True,
            'likes': new_count
        }))
        
        response = LikeService.create_liked_response(response, liked_courses)
        return response
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/courses/<course_id>/likes')
def get_course_likes(course_id):
    """API endpoint to get likes for a course"""
    try:
        likes = LikeService.get_course_likes(course_id)
        return jsonify({
            'success': True,
            'likes': likes
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500