from flask import Blueprint, render_template, request, abort, make_response, jsonify
from ..services.course_service import CourseService
from ..services.progress_service import UserProgressService
from ..services.search_service import SearchService
from ..utils.helpers import sanitize_path

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page - list all courses"""
    courses = CourseService.get_all_courses()
    return render_template('index.html', courses=courses)

@main_bp.route('/course/<course_id>')
def course(course_id):
    """Course page - show course details and documents"""
    # Security check
    if not sanitize_path(course_id):
        abort(404)
    
    # Check if course exists
    course = CourseService._load_course_info(course_id)
    if not course:
        abort(404)
    
    docs = CourseService.get_course_documents(course_id)
    
    # Get user progress for this course
    user_progress = UserProgressService.get_user_progress(course_id)
    completed_docs = len(user_progress)
    
    return render_template(
        'course.html', 
        course=course, 
        docs=docs, 
        completed_docs=completed_docs, 
        user_progress=user_progress
    )

@main_bp.route('/course/<course_id>/document/<filename>')
def course_document(course_id, filename):
    """Document page - show a specific document"""
    # Security check
    if not sanitize_path(course_id) or not sanitize_path(filename):
        abort(404)
    
    doc_data, error = CourseService.read_course_document(course_id, filename)
    if error:
        abort(404)
    
    docs = CourseService.get_course_documents(course_id)
    
    # Get course info for breadcrumb
    course = CourseService._load_course_info(course_id)
    
    # Update user progress
    response = make_response(render_template(
        'document.html', 
        course=course, 
        doc=doc_data, 
        docs=docs, 
        filename=filename
    ))
    
    # Set cookie to track progress
    progress = UserProgressService.add_document_to_progress(course_id, filename)
    response = UserProgressService.create_progress_response(response, course_id, progress)
    
    return response

@main_bp.route('/search')
def search():
    """Search page - search documents"""
    query = request.args.get('q', '').strip()
    results = SearchService.search_documents(query) if query else []
    courses = CourseService.get_all_courses()
    
    return render_template(
        'search.html', 
        courses=courses, 
        results=results, 
        query=query
    )