from flask import Flask, render_template, request, abort, redirect, url_for, session, flash, send_from_directory, make_response, jsonify
import os
import markdown
import re
import json
import hashlib
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'academic_portal_secret_key_2025'  # Change this in production

# Add datetime filter for Jinja2 templates
@app.template_filter('datetime')
def format_datetime(timestamp):
    import datetime
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')

# Add index filter for Jinja2 templates
@app.template_filter('index')
def index_filter(lst, item):
    try:
        return lst.index(item)
    except ValueError:
        return -1

# Configuration
COURSES_FOLDER = os.path.join(app.root_path, 'courses')
STATIC_FOLDER = os.path.join(app.root_path, 'static')
FILE_STORAGE_FOLDER = os.path.join(app.root_path, 'file_storage')

# File storage configuration
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'zip', 'rar', 'mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv', 'webm', 'mp3', 'wav', 'py', 'js', 'html', 'css', 'java', 'cpp', 'c', 'php', 'rb', 'swift', 'go', 'sql', 'json', 'xml', 'yml', 'yaml', 'md', 'csv'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# Ensure file storage directory exists
os.makedirs(FILE_STORAGE_FOLDER, exist_ok=True)

# Default admin credentials (username: admin, password: password)
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'password'

def get_courses_list():
    """Get list of all courses"""
    courses = []
    if os.path.exists(COURSES_FOLDER):
        for course_dir in os.listdir(COURSES_FOLDER):
            course_path = os.path.join(COURSES_FOLDER, course_dir)
            if os.path.isdir(course_path):
                # Check if course.json exists
                course_info_path = os.path.join(course_path, 'course.json')
                course_info = {
                    'id': course_dir,
                    'title': course_dir.replace('_', ' ').replace('-', ' ').title(),
                    'description': 'No description available',
                    'instructor': 'Unknown'
                }
                
                if os.path.exists(course_info_path):
                    try:
                        with open(course_info_path, 'r') as f:
                            course_data = json.load(f)
                            course_info.update(course_data)
                    except:
                        pass
                
                # Count documents
                docs_count = 0
                if os.path.exists(os.path.join(course_path, 'docs')):
                    for filename in os.listdir(os.path.join(course_path, 'docs')):
                        if filename.endswith('.md'):
                            docs_count += 1
                
                course_info['docs_count'] = docs_count
                courses.append(course_info)
    return sorted(courses, key=lambda x: x['title'])

def get_course_docs(course_id):
    """Get list of documents for a specific course"""
    docs = []
    course_docs_path = os.path.join(COURSES_FOLDER, course_id, 'docs')
    
    if os.path.exists(course_docs_path):
        for filename in os.listdir(course_docs_path):
            if filename.endswith('.md'):
                # Remove .md extension and replace underscores/hyphens with spaces
                title = os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ')
                # Capitalize first letter of each word
                title = ' '.join(word.capitalize() for word in title.split())
                docs.append({
                    'filename': filename,
                    'title': title
                })
    return sorted(docs, key=lambda x: x['title'])

def read_course_doc(course_id, filename):
    """Read and parse markdown document from a course"""
    filepath = os.path.join(COURSES_FOLDER, course_id, 'docs', filename)
    if not os.path.exists(filepath):
        return None, "Document not found"
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Convert markdown to HTML
        md = markdown.Markdown(extensions=['fenced_code', 'tables', 'toc'])
        html_content = md.convert(content)
        
        # Extract title from first line if it's a header
        title = filename
        lines = content.split('\n')
        if lines and lines[0].startswith('#'):
            title = lines[0].lstrip('# ').strip()
        else:
            # Remove .md extension and format
            title = os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ')
            title = ' '.join(word.capitalize() for word in title.split())
            
        return {
            'title': title,
            'content': html_content,
            'toc': getattr(md, 'toc', '')
        }, None
    except Exception as e:
        return None, f"Error reading document: {str(e)}"

def save_course_info(course_id, course_data):
    """Save course information to course.json"""
    course_path = os.path.join(COURSES_FOLDER, course_id)
    if not os.path.exists(course_path):
        os.makedirs(course_path)
    
    course_info_path = os.path.join(course_path, 'course.json')
    try:
        with open(course_info_path, 'w') as f:
            json.dump(course_data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving course info: {e}")
        return False

def save_document(course_id, filename, content):
    """Save a document to a course"""
    course_docs_path = os.path.join(COURSES_FOLDER, course_id, 'docs')
    if not os.path.exists(course_docs_path):
        os.makedirs(course_docs_path)
    
    filepath = os.path.join(course_docs_path, filename)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error saving document: {e}")
        return False

def delete_document(course_id, filename):
    """Delete a document from a course"""
    filepath = os.path.join(COURSES_FOLDER, course_id, 'docs', filename)
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            return True
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False
    return False

def is_logged_in():
    """Check if user is logged in as admin"""
    return session.get('admin_logged_in', False)

def get_user_progress(course_id):
    """Get user's progress for a specific course from cookies"""
    progress_key = f"course_progress_{course_id}"
    progress_data = request.cookies.get(progress_key, "{}")
    try:
        return json.loads(progress_data)
    except:
        return {}

def set_user_progress(course_id, doc_filename):
    """Add a document to user's progress for a course"""
    progress_key = f"course_progress_{course_id}"
    progress = get_user_progress(course_id)
    if doc_filename not in progress:
        progress[doc_filename] = True
    return progress

def get_user_progress(course_id):
    """Get user's progress for a specific course from cookies"""
    progress_key = f"course_progress_{course_id}"
    progress_data = request.cookies.get(progress_key, "{}")
    try:
        return json.loads(progress_data)
    except:
        return {}

def set_user_progress(course_id, doc_filename):
    """Add a document to user's progress for a course"""
    progress_key = f"course_progress_{course_id}"
    progress = get_user_progress(course_id)
    if doc_filename not in progress:
        progress[doc_filename] = True
    return progress

@app.route('/')
def index():
    courses = get_courses_list()
    return render_template('index.html', courses=courses)

@app.route('/course/<course_id>')
def course(course_id):
    # Security check
    if '..' in course_id or course_id.startswith('/'):
        abort(404)
    
    # Check if course exists
    course_path = os.path.join(COURSES_FOLDER, course_id)
    if not os.path.exists(course_path):
        abort(404)
    
    # Get course info
    course_info_path = os.path.join(course_path, 'course.json')
    course_info = {
        'id': course_id,
        'title': course_id.replace('_', ' ').replace('-', ' ').title(),
        'description': 'No description available',
        'instructor': 'Unknown'
    }
    
    if os.path.exists(course_info_path):
        try:
            with open(course_info_path, 'r') as f:
                course_data = json.load(f)
                course_info.update(course_data)
        except:
            pass
    
    docs = get_course_docs(course_id)
    
    # Get user progress for this course
    user_progress = get_user_progress(course_id)
    completed_docs = len(user_progress)
    
    return render_template('course.html', course=course_info, docs=docs, completed_docs=completed_docs)

@app.route('/course/<course_id>/document/<filename>')
def course_document(course_id, filename):
    # Security check
    if '..' in course_id or course_id.startswith('/') or '..' in filename or filename.startswith('/'):
        abort(404)
    
    # Check if course exists
    course_path = os.path.join(COURSES_FOLDER, course_id)
    if not os.path.exists(course_path):
        abort(404)
    
    doc_data, error = read_course_doc(course_id, filename)
    if error:
        abort(404)
    
    docs = get_course_docs(course_id)
    
    # Get course info for breadcrumb
    course_info_path = os.path.join(course_path, 'course.json')
    course_info = {
        'id': course_id,
        'title': course_id.replace('_', ' ').replace('-', ' ').title()
    }
    
    if os.path.exists(course_info_path):
        try:
            with open(course_info_path, 'r') as f:
                course_data = json.load(f)
                course_info.update(course_data)
        except:
            pass
    
    # Update user progress
    response = make_response(render_template('document.html', course=course_info, doc=doc_data, docs=docs, filename=filename))
    
    # Set cookie to track progress
    progress = set_user_progress(course_id, filename)
    progress_key = f"course_progress_{course_id}"
    response.set_cookie(progress_key, json.dumps(progress), max_age=30*24*60*60)  # 30 days
    
    return response

@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    results = []
    
    if query and os.path.exists(COURSES_FOLDER):
        # Search across all courses
        for course_dir in os.listdir(COURSES_FOLDER):
            course_path = os.path.join(COURSES_FOLDER, course_dir)
            if os.path.isdir(course_path):
                course_docs_path = os.path.join(course_path, 'docs')
                if os.path.exists(course_docs_path):
                    for filename in os.listdir(course_docs_path):
                        if filename.endswith('.md'):
                            filepath = os.path.join(course_docs_path, filename)
                            try:
                                with open(filepath, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                
                                # Check if query is in content (case insensitive)
                                if re.search(query, content, re.IGNORECASE):
                                    # Extract title
                                    lines = content.split('\n')
                                    title = filename
                                    if lines and lines[0].startswith('#'):
                                        title = lines[0].lstrip('# ').strip()
                                    else:
                                        title = os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ')
                                        title = ' '.join(word.capitalize() for word in title.split())
                                    
                                    # Get course info
                                    course_info_path = os.path.join(course_path, 'course.json')
                                    course_title = course_dir.replace('_', ' ').replace('-', ' ').title()
                                    if os.path.exists(course_info_path):
                                        try:
                                            with open(course_info_path, 'r') as f:
                                                course_data = json.load(f)
                                                course_title = course_data.get('title', course_title)
                                        except:
                                            pass
                                    
                                    # Create snippet
                                    content_lower = content.lower()
                                    query_lower = query.lower()
                                    index = content_lower.find(query_lower)
                                    start = max(0, index - 50)
                                    end = min(len(content), index + 200)
                                    snippet = content[start:end]
                                    if start > 0:
                                        snippet = '...' + snippet
                                    if end < len(content):
                                        snippet = snippet + '...'
                                    
                                    results.append({
                                        'course_id': course_dir,
                                        'filename': filename,
                                        'title': title,
                                        'course_title': course_title,
                                        'snippet': snippet
                                    })
                            except Exception:
                                continue
    
    courses = get_courses_list()
    return render_template('search.html', courses=courses, results=results, query=query)

# Admin Routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check credentials (in a real app, you'd use a proper authentication system)
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('Successfully logged in as administrator', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/admin')
def admin_dashboard():
    if not is_logged_in():
        return redirect(url_for('admin_login'))
    
    courses = get_courses_list()
    total_courses = len(courses)
    
    # Count total documents
    total_documents = 0
    for course in courses:
        total_documents += course.get('docs_count', 0)
    
    return render_template('admin/dashboard.html', 
                          courses=courses, 
                          total_courses=total_courses, 
                          total_documents=total_documents)

@app.route('/admin/courses')
def admin_courses():
    if not is_logged_in():
        return redirect(url_for('admin_login'))
    
    courses = get_courses_list()
    return render_template('admin/courses.html', courses=courses)

@app.route('/admin/course/<course_id>')
def admin_course_view(course_id):
    if not is_logged_in():
        return redirect(url_for('admin_login'))
    
    # Security check
    if '..' in course_id or course_id.startswith('/'):
        abort(404)
    
    # Check if course exists
    course_path = os.path.join(COURSES_FOLDER, course_id)
    if not os.path.exists(course_path):
        abort(404)
    
    # Get course info
    course_info_path = os.path.join(course_path, 'course.json')
    course_info = {
        'id': course_id,
        'title': course_id.replace('_', ' ').replace('-', ' ').title(),
        'description': 'No description available',
        'instructor': 'Unknown'
    }
    
    if os.path.exists(course_info_path):
        try:
            with open(course_info_path, 'r') as f:
                course_data = json.load(f)
                course_info.update(course_data)
        except:
            pass
    
    docs = get_course_docs(course_id)
    return render_template('admin/course_view.html', course=course_info, docs=docs)

@app.route('/admin/course/new', methods=['GET', 'POST'])
def admin_course_new():
    if not is_logged_in():
        return redirect(url_for('admin_login'))
    
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
            course_path = os.path.join(COURSES_FOLDER, course_id)
            if os.path.exists(course_path):
                flash('A course with this ID already exists', 'error')
            else:
                os.makedirs(os.path.join(course_path, 'docs'))
                
                # Save course info
                course_data = {
                    'title': title,
                    'description': description,
                    'instructor': instructor,
                    'duration': duration,
                    'level': level
                }
                
                if save_course_info(course_id, course_data):
                    flash(f'Course "{title}" created successfully', 'success')
                    return redirect(url_for('admin_course_view', course_id=course_id))
                else:
                    flash('Error creating course', 'error')
    
    return render_template('admin/course_form.html', course=None)

@app.route('/admin/course/<course_id>/edit', methods=['GET', 'POST'])
def admin_course_edit(course_id):
    if not is_logged_in():
        return redirect(url_for('admin_login'))
    
    # Security check
    if '..' in course_id or course_id.startswith('/'):
        abort(404)
    
    course_path = os.path.join(COURSES_FOLDER, course_id)
    if not os.path.exists(course_path):
        abort(404)
    
    # Get course info
    course_info_path = os.path.join(course_path, 'course.json')
    course_info = {
        'id': course_id,
        'title': course_id.replace('_', ' ').replace('-', ' ').title(),
        'description': '',
        'instructor': '',
        'duration': '',
        'level': ''
    }
    
    if os.path.exists(course_info_path):
        try:
            with open(course_info_path, 'r') as f:
                course_data = json.load(f)
                course_info.update(course_data)
        except:
            pass
    
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
            
            if save_course_info(course_id, course_data):
                flash(f'Course "{title}" updated successfully', 'success')
                return redirect(url_for('admin_course_view', course_id=course_id))
            else:
                flash('Error updating course', 'error')
    
    return render_template('admin/course_form.html', course=course_info)

@app.route('/admin/course/<course_id>/document/new', methods=['GET', 'POST'])
def admin_document_new(course_id):
    if not is_logged_in():
        return redirect(url_for('admin_login'))
    
    # Security check
    if '..' in course_id or course_id.startswith('/'):
        abort(404)
    
    course_path = os.path.join(COURSES_FOLDER, course_id)
    if not os.path.exists(course_path):
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
            if save_document(course_id, filename, content):
                flash(f'Document "{title}" created successfully', 'success')
                return redirect(url_for('admin_course_view', course_id=course_id))
            else:
                flash('Error creating document', 'error')
    
    return render_template('admin/document_form.html', course_id=course_id, document=None)

@app.route('/admin/course/<course_id>/document/<filename>/edit', methods=['GET', 'POST'])
def admin_document_edit(course_id, filename):
    if not is_logged_in():
        return redirect(url_for('admin_login'))
    
    # Security check
    if '..' in course_id or course_id.startswith('/') or '..' in filename or filename.startswith('/'):
        abort(404)
    
    course_path = os.path.join(COURSES_FOLDER, course_id)
    if not os.path.exists(course_path):
        abort(404)
    
    # Read document
    filepath = os.path.join(course_path, 'docs', filename)
    if not os.path.exists(filepath):
        abort(404)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        flash(f'Error reading document: {e}', 'error')
        return redirect(url_for('admin_course_view', course_id=course_id))
    
    # Extract title from first line if it's a header
    lines = content.split('\n')
    doc_title = filename
    if lines and lines[0].startswith('#'):
        doc_title = lines[0].lstrip('# ').strip()
    else:
        # Remove .md extension and format
        doc_title = os.path.splitext(filename)[0].replace('-', ' ').replace('_', ' ')
        doc_title = ' '.join(word.capitalize() for word in doc_title.split())
    
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
            if save_document(course_id, filename, new_content):
                flash(f'Document "{new_title}" updated successfully', 'success')
                return redirect(url_for('admin_course_view', course_id=course_id))
            else:
                flash('Error updating document', 'error')
    
    return render_template('admin/document_form.html', course_id=course_id, document=document)

@app.route('/admin/course/<course_id>/document/<filename>/delete', methods=['POST'])
def admin_document_delete(course_id, filename):
    if not is_logged_in():
        return redirect(url_for('admin_login'))
    
    # Security check
    if '..' in course_id or course_id.startswith('/') or '..' in filename or filename.startswith('/'):
        abort(404)
    
    if delete_document(course_id, filename):
        flash('Document deleted successfully', 'success')
    else:
        flash('Error deleting document', 'error')
    
    return redirect(url_for('admin_course_view', course_id=course_id))

# File Storage Routes
@app.route('/admin/file-storage')
def admin_file_storage():
    if not is_logged_in():
        return redirect(url_for('admin_login'))
    
    files = get_file_storage_files()
    return render_template('admin/file_storage.html', files=files)

@app.route('/admin/file-storage/upload', methods=['POST'])
def admin_file_storage_upload():
    if not is_logged_in():
        return redirect(url_for('admin_login'))
    
    uploaded_files = request.files.getlist('file')
    
    if not uploaded_files or all(f.filename == '' for f in uploaded_files):
        flash('No file selected', 'error')
        return redirect(url_for('admin_file_storage'))
    
    success_count = 0
    error_count = 0
    
    for file in uploaded_files:
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Check if file already exists
            if os.path.exists(os.path.join(FILE_STORAGE_FOLDER, filename)):
                filename = generate_unique_filename(filename)
            
            try:
                file.save(os.path.join(FILE_STORAGE_FOLDER, filename))
                success_count += 1
            except Exception as e:
                print(f"Error saving file {filename}: {e}")
                error_count += 1
        else:
            error_count += 1
    
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
    
    return redirect(url_for('admin_file_storage'))

@app.route('/admin/file-storage/<filename>/delete', methods=['POST'])
def admin_file_storage_delete(filename):
    if not is_logged_in():
        return redirect(url_for('admin_login'))
    
    # Security check
    if '..' in filename or filename.startswith('/'):
        abort(404)
    
    filepath = os.path.join(FILE_STORAGE_FOLDER, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        # Also remove public flag file if exists
        flag_path = os.path.join(FILE_STORAGE_FOLDER, f"{filename}.public")
        if os.path.exists(flag_path):
            os.remove(flag_path)
        flash(f'File "{filename}" deleted successfully', 'success')
    else:
        flash('File not found', 'error')
    
    return redirect(url_for('admin_file_storage'))

@app.route('/admin/file-storage/<filename>/toggle-public', methods=['POST'])
def admin_file_storage_toggle_public(filename):
    if not is_logged_in():
        return redirect(url_for('admin_login'))
    
    # Security check
    if '..' in filename or filename.startswith('/'):
        abort(404)
    
    filepath = os.path.join(FILE_STORAGE_FOLDER, filename)
    if os.path.exists(filepath):
        # Check current public status
        is_public = os.path.exists(os.path.join(FILE_STORAGE_FOLDER, f"{filename}.public"))
        # Toggle public status
        set_file_public(filename, not is_public)
        status = "public" if not is_public else "private"
        flash(f'File "{filename}" is now {status}', 'success')
    else:
        flash('File not found', 'error')
    
    return redirect(url_for('admin_file_storage'))

# Public file access route (for files marked as public)
@app.route('/file/<filename>')
def public_file(filename):
    # Security check
    if '..' in filename or filename.startswith('/'):
        abort(404)
    
    filepath = os.path.join(FILE_STORAGE_FOLDER, filename)
    if not os.path.exists(filepath):
        abort(404)
    
    # Check if file is marked as public
    public_flag = os.path.join(FILE_STORAGE_FOLDER, f"{filename}.public")
    if not os.path.exists(public_flag):
        # File is not public, check if user is admin
        if not is_logged_in():
            abort(403)  # Forbidden
    
    return send_from_directory(FILE_STORAGE_FOLDER, filename)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_filename(filename):
    """Generate a unique filename to prevent conflicts"""
    name, ext = os.path.splitext(filename)
    unique_name = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
    return unique_name

def get_file_storage_files():
    """Get list of all files in file storage"""
    files = []
    if os.path.exists(FILE_STORAGE_FOLDER):
        for filename in os.listdir(FILE_STORAGE_FOLDER):
            filepath = os.path.join(FILE_STORAGE_FOLDER, filename)
            if os.path.isfile(filepath) and not filename.endswith('.public'):
                stat = os.stat(filepath)
                files.append({
                    'filename': filename,
                    'size': stat.st_size,
                    'modified': stat.st_mtime,
                    'is_public': os.path.exists(os.path.join(FILE_STORAGE_FOLDER, f"{filename}.public"))
                })
    return sorted(files, key=lambda x: x['modified'], reverse=True)

@app.route('/api/user-progress')
def api_user_progress():
    """API endpoint to get user's progress for all courses"""
    courses = get_courses_list()
    progress_data = {}
    
    for course in courses:
        user_progress = get_user_progress(course['id'])
        completed_docs = len(user_progress)
        progress_data[course['id']] = {
            'completed': completed_docs,
            'total': course['docs_count'],
            'percentage': int((completed_docs / course['docs_count'] * 100)) if course['docs_count'] > 0 else 0
        }
    
    return jsonify(progress_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)