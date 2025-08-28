from flask import Blueprint, render_template, request, abort, redirect, url_for, flash
from ..services.course_service import CourseService
from ..services.file_service import FileStorageService
from ..services.auth_service import AuthService
from ..utils.helpers import sanitize_path
from .. import cache

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check credentials
        if AuthService.authenticate(username, password):
            AuthService.login()
            flash('Successfully logged in as administrator', 'success')
            return redirect(url_for('admin.admin_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('admin/login.html')

@admin_bp.route('/logout')
def admin_logout():
    """Admin logout"""
    AuthService.logout()
    flash('You have been logged out', 'info')
    return redirect(url_for('main.index'))

@admin_bp.route('/')
def admin_dashboard():
    """Admin dashboard"""
    if not AuthService.is_logged_in():
        return redirect(url_for('admin.admin_login'))
    
    courses = CourseService.get_all_courses()
    total_courses = len(courses)
    
    # Count total documents
    total_documents = sum(course.docs_count for course in courses)
    
    return render_template(
        'admin/dashboard.html',
        courses=courses,
        total_courses=total_courses,
        total_documents=total_documents
    )

@admin_bp.route('/courses')
def admin_courses():
    """Admin courses list"""
    if not AuthService.is_logged_in():
        return redirect(url_for('admin.admin_login'))
    
    courses = CourseService.get_all_courses()
    return render_template('admin/courses.html', courses=courses)

@admin_bp.route('/course/<course_id>')
def admin_course_view(course_id):
    """Admin course view"""
    if not AuthService.is_logged_in():
        return redirect(url_for('admin.admin_login'))
    
    # Security check
    if not sanitize_path(course_id):
        abort(404)
    
    # Check if course exists
    course = CourseService._load_course_info(course_id)
    if not course:
        abort(404)
    
    docs = CourseService.get_course_documents(course_id)
    return render_template('admin/course_view.html', course=course, docs=docs)

@admin_bp.route('/course/new', methods=['GET', 'POST'])
def admin_course_new():
    """Admin create new course"""
    if not AuthService.is_logged_in():
        return redirect(url_for('admin.admin_login'))
    
    if request.method == 'POST':
        course_id = request.form['course_id'].strip().replace(' ', '_').lower()
        title = request.form['title'].strip()
        description = request.form['description'].strip()
        instructor = request.form['instructor'].strip()
        duration = request.form['duration'].strip()
        level = request.form['level'].strip()
        
        if not course_id or not title:
            flash('Course ID and title are required', 'error')
        else:
            # Create course directory structure
            from ..config.settings import Config
            course_path = Config.COURSES_FOLDER / course_id
            if course_path.exists():
                flash('A course with this ID already exists', 'error')
            else:
                (course_path / 'docs').mkdir(parents=True, exist_ok=True)
                
                # Save course info
                course_data = {
                    'title': title,
                    'description': description,
                    'instructor': instructor,
                    'duration': duration,
                    'level': level
                }
                
                if CourseService.save_course_info(course_id, course_data):
                    # Clear cache after creating a new course
                    cache.clear()
                    flash(f'Course "{title}" created successfully', 'success')
                    return redirect(url_for('admin.admin_course_view', course_id=course_id))
                else:
                    flash('Error creating course', 'error')
    
    return render_template('admin/course_form.html', course=None)

@admin_bp.route('/course/<course_id>/edit', methods=['GET', 'POST'])
def admin_course_edit(course_id):
    """Admin edit course"""
    if not AuthService.is_logged_in():
        return redirect(url_for('admin.admin_login'))
    
    # Security check
    if not sanitize_path(course_id):
        abort(404)
    
    from ..config.settings import Config
    course_path = Config.COURSES_FOLDER / course_id
    if not course_path.exists():
        abort(404)
    
    # Get course info
    course = CourseService._load_course_info(course_id)
    
    if request.method == 'POST':
        title = request.form['title'].strip()
        description = request.form['description'].strip()
        instructor = request.form['instructor'].strip()
        duration = request.form['duration'].strip()
        level = request.form['level'].strip()
        
        if not title:
            flash('Title is required', 'error')
        else:
            # Save course info
            course_data = {
                'title': title,
                'description': description,
                'instructor': instructor,
                'duration': duration,
                'level': level
            }
            
            if CourseService.save_course_info(course_id, course_data):
                # Clear cache after updating a course
                cache.clear()
                flash(f'Course "{title}" updated successfully', 'success')
                return redirect(url_for('admin.admin_course_view', course_id=course_id))
            else:
                flash('Error updating course', 'error')
    
    return render_template('admin/course_form.html', course=course)

@admin_bp.route('/course/<course_id>/document/new', methods=['GET', 'POST'])
def admin_document_new(course_id):
    """Admin create new document"""
    if not AuthService.is_logged_in():
        return redirect(url_for('admin.admin_login'))
    
    # Security check
    if not sanitize_path(course_id):
        abort(404)
    
    from ..config.settings import Config
    course_path = Config.COURSES_FOLDER / course_id
    if not course_path.exists():
        abort(404)
    
    if request.method == 'POST':
        title = request.form['title'].strip()
        content = request.form['content'].strip()
        
        if not title:
            flash('Document title is required', 'error')
        else:
            # Create filename from title
            filename = title.lower().replace(' ', '-').replace('_', '-') + '.md'
            
            # Save document
            if CourseService.save_document(course_id, filename, content):
                # Clear cache after creating a new document
                cache.clear()
                flash(f'Document "{title}" created successfully', 'success')
                return redirect(url_for('admin.admin_course_view', course_id=course_id))
            else:
                flash('Error creating document', 'error')
    
    return render_template('admin/document_form.html', course_id=course_id, document=None)

@admin_bp.route('/course/<course_id>/document/<filename>/edit', methods=['GET', 'POST'])
def admin_document_edit(course_id, filename):
    """Admin edit document"""
    if not AuthService.is_logged_in():
        return redirect(url_for('admin.admin_login'))
    
    # Security check
    if not sanitize_path(course_id) or not sanitize_path(filename):
        abort(404)
    
    from ..config.settings import Config
    course_path = Config.COURSES_FOLDER / course_id
    if not course_path.exists():
        abort(404)
    
    # Read document
    filepath = course_path / 'docs' / filename
    if not filepath.exists():
        abort(404)
    
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception as e:
        flash(f'Error reading document: {e}', 'error')
        return redirect(url_for('admin.admin_course_view', course_id=course_id))
    
    # Extract title from first line if it's a header
    from ..utils.helpers import extract_title_from_markdown
    doc_title = extract_title_from_markdown(content, filename)
    
    document = {
        'filename': filename,
        'title': doc_title,
        'content': content
    }
    
    if request.method == 'POST':
        new_title = request.form['title'].strip()
        new_content = request.form['content'].strip()
        
        if not new_title:
            flash('Document title is required', 'error')
        else:
            # Update document
            if CourseService.save_document(course_id, filename, new_content):
                # Clear cache after updating a document
                cache.clear()
                flash(f'Document "{new_title}" updated successfully', 'success')
                return redirect(url_for('admin.admin_course_view', course_id=course_id))
            else:
                flash('Error updating document', 'error')
    
    return render_template('admin/document_form.html', course_id=course_id, document=document)

@admin_bp.route('/course/<course_id>/document/<filename>/delete', methods=['POST'])
def admin_document_delete(course_id, filename):
    """Admin delete document"""
    if not AuthService.is_logged_in():
        return redirect(url_for('admin.admin_login'))
    
    # Security check
    if not sanitize_path(course_id) or not sanitize_path(filename):
        abort(404)
    
    if CourseService.delete_document(course_id, filename):
        # Clear cache after deleting a document
        cache.clear()
        flash('Document deleted successfully', 'success')
    else:
        flash('Error deleting document', 'error')
    
    return redirect(url_for('admin.admin_course_view', course_id=course_id))

# File Storage Routes
@admin_bp.route('/file-storage')
def admin_file_storage():
    """Admin file storage"""
    if not AuthService.is_logged_in():
        return redirect(url_for('admin.admin_login'))
    
    files = FileStorageService.get_all_files()
    return render_template('admin/file_storage.html', files=files)

@admin_bp.route('/file-storage/upload', methods=['POST'])
def admin_file_storage_upload():
    """Admin upload files"""
    if not AuthService.is_logged_in():
        return redirect(url_for('admin.admin_login'))
    
    uploaded_files = request.files.getlist('file')
    
    success_count, error_count = FileStorageService.upload_files(uploaded_files)
    
    if success_count > 0:
        if success_count == 1:
            flash(f'File uploaded successfully', 'success')
        else:
            flash(f'{success_count} files uploaded successfully', 'success')
    
    if error_count > 0:
        if error_count == 1:
            flash(f'Failed to upload 1 file', 'error')
        else:
            flash(f'Failed to upload {error_count} files', 'error')
    
    return redirect(url_for('admin.admin_file_storage'))

@admin_bp.route('/file-storage/<filename>/delete', methods=['POST'])
def admin_file_storage_delete(filename):
    """Admin delete file"""
    if not AuthService.is_logged_in():
        return redirect(url_for('admin.admin_login'))
    
    # Security check
    if not sanitize_path(filename):
        abort(404)
    
    if FileStorageService.delete_file(filename):
        flash(f'File "{filename}" deleted successfully', 'success')
    else:
        flash('File not found', 'error')
    
    return redirect(url_for('admin.admin_file_storage'))

@admin_bp.route('/file-storage/<filename>/toggle-public', methods=['POST'])
def admin_file_storage_toggle_public(filename):
    """Admin toggle file public status"""
    if not AuthService.is_logged_in():
        return redirect(url_for('admin.admin_login'))
    
    # Security check
    if not sanitize_path(filename):
        abort(404)
    
    if FileStorageService.toggle_public_status(filename):
        # Check current public status for message
        is_public = FileStorageService.is_file_public(filename)
        status = "public" if is_public else "private"
        flash(f'File "{filename}" is now {status}', 'success')
    else:
        flash('File not found', 'error')
    
    return redirect(url_for('admin.admin_file_storage'))

# Public file access route (for files marked as public)
@admin_bp.route('/file/<filename>')
def public_file(filename):
    """Serve public files"""
    # Security check
    if not sanitize_path(filename):
        abort(404)
    
    from ..config.settings import Config
    from flask import send_from_directory
    
    filepath = Config.FILE_STORAGE_FOLDER / filename
    if not filepath.exists():
        abort(404)
    
    # Check if file is marked as public
    if not FileStorageService.is_file_public(filename):
        # File is not public, check if user is admin
        if not AuthService.is_logged_in():
            abort(403)  # Forbidden
    
    return send_from_directory(str(Config.FILE_STORAGE_FOLDER), filename)