from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file, abort
import os
import markdown
import json
import re
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Configure Markdown
md = markdown.Markdown(extensions=['fenced_code', 'tables', 'toc', 'codehilite'])

# Configuration
DOCS_DIR = os.path.join(os.path.dirname(__file__), 'docs')
DEFAULT_DOC = '1. welcome.md'
MEDIA_DIR = "media"

# Admin credentials (in production, use proper authentication)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

# Helper functions
def authenticate_admin(username, password):
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD

def get_courses():
    """Return a list of courses (directories) in the docs directory."""
    if not os.path.exists(DOCS_DIR):
        return []
    courses = []
    for item in os.listdir(DOCS_DIR):
        course_path = os.path.join(DOCS_DIR, item)
        if os.path.isdir(course_path):
            # Try to read course info
            info_file = os.path.join(course_path, "info.txt")
            description = ""
            if os.path.exists(info_file):
                with open(info_file, 'r') as f:
                    description = f.read().strip()
            courses.append({
                "name": item,
                "description": description
            })
    return courses

def get_markdown_file_list(course_dir):
    """Return a sorted list of markdown files in the course directory."""
    course_path = os.path.join(DOCS_DIR, course_dir)
    if not os.path.exists(course_path):
        return []
    return sorted(
        [f for f in os.listdir(course_path) if f.endswith('.md')],
        key=lambda x: x.lower()
    )

def count_documents_in_course(course_dir):
    """Count the number of markdown documents in a course."""
    return len(get_markdown_file_list(course_dir))

def get_courses_with_document_counts():
    """Return a list of courses with document counts."""
    if not os.path.exists(DOCS_DIR):
        return []
    courses = []
    total_documents = 0
    for item in os.listdir(DOCS_DIR):
        course_path = os.path.join(DOCS_DIR, item)
        if os.path.isdir(course_path):
            # Try to read course info
            info_file = os.path.join(course_path, "info.txt")
            description = ""
            if os.path.exists(info_file):
                with open(info_file, 'r') as f:
                    description = f.read().strip()
            
            # Count documents in this course
            doc_count = count_documents_in_course(item)
            total_documents += doc_count
            
            courses.append({
                "name": item,
                "description": description,
                "document_count": doc_count
            })
    return courses, total_documents

def render_markdown_file(course_dir, filename):
    """Convert markdown file content to HTML."""
    filepath = os.path.join(DOCS_DIR, course_dir, filename)
    if not os.path.exists(filepath):
        abort(404, f"File {filename} not found")
    with open(filepath, 'r', encoding='utf-8') as f:
        md_content = f.read()
    return markdown.markdown(
        md_content,
        extensions=['fenced_code', 'tables', 'toc', 'codehilite']
    )

def create_course(course_name, description=""):
    """Create a new course directory with info.txt file."""
    course_path = os.path.join(DOCS_DIR, course_name)
    if not os.path.exists(course_path):
        os.makedirs(course_path)
        # Create info.txt file
        info_file = os.path.join(course_path, "info.txt")
        with open(info_file, 'w') as f:
            f.write(description)
        # Create welcome.md file
        welcome_file = os.path.join(course_path, "1. welcome.md")
        with open(welcome_file, 'w') as f:
            f.write(f"# Welcome to {course_name}\n\nThis is the beginning of your {course_name} documentation.")
        return True
    return False

def delete_course(course_name):
    """Delete a course directory."""
    course_path = os.path.join(DOCS_DIR, course_name)
    if os.path.exists(course_path) and os.path.isdir(course_path):
        import shutil
        shutil.rmtree(course_path)
        return True
    return False

def create_document(course_name, filename, content):
    """Create a new document in a course."""
    course_path = os.path.join(DOCS_DIR, course_name)
    if not os.path.exists(course_path):
        return False
    filepath = os.path.join(course_path, filename)
    with open(filepath, 'w') as f:
        f.write(content)
    return True

def update_document(course_name, filename, content):
    """Update an existing document in a course."""
    course_path = os.path.join(DOCS_DIR, course_name)
    filepath = os.path.join(course_path, filename)
    if os.path.exists(filepath):
        with open(filepath, 'w') as f:
            f.write(content)
        return True
    return False

def delete_document(course_name, filename):
    """Delete a document from a course."""
    course_path = os.path.join(DOCS_DIR, course_name)
    filepath = os.path.join(course_path, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False

def get_document_content(course_name, filename):
    """Get the content of a document."""
    course_path = os.path.join(DOCS_DIR, course_name)
    filepath = os.path.join(course_path, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return f.read()
    return None

def search_documents(query):
    """Search for a query across all documents in all courses."""
    results = []
    if not os.path.exists(DOCS_DIR):
        return results
    
    # Escape special regex characters in the query
    escaped_query = re.escape(query)
    
    for course in os.listdir(DOCS_DIR):
        course_path = os.path.join(DOCS_DIR, course)
        if os.path.isdir(course_path):
            for filename in os.listdir(course_path):
                if filename.endswith('.md'):
                    filepath = os.path.join(course_path, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Check if query is in content (case insensitive)
                            if re.search(escaped_query, content, re.IGNORECASE):
                                # Get a snippet of the content around the match
                                lines = content.split('\n')
                                for i, line in enumerate(lines):
                                    if re.search(escaped_query, line, re.IGNORECASE):
                                        # Get a few lines before and after for context
                                        start = max(0, i - 2)
                                        end = min(len(lines), i + 3)
                                        excerpt = '\n'.join(lines[start:end])
                                        
                                        results.append({
                                            'course': course,
                                            'document': filename.replace('.md', ''),
                                            'excerpt': excerpt.strip()
                                        })
                                        break  # Only add the first match per document
                    except Exception as e:
                        # Skip files that can't be read
                        continue
    return results

def get_all_documents():
    """Get a list of all documents across all courses."""
    documents = []
    if not os.path.exists(DOCS_DIR):
        return documents
    
    for course in os.listdir(DOCS_DIR):
        course_path = os.path.join(DOCS_DIR, course)
        if os.path.isdir(course_path):
            for filename in os.listdir(course_path):
                if filename.endswith('.md'):
                    documents.append({
                        'course': course,
                        'document': filename.replace('.md', ''),
                        'url': f'/docs/{course}/{filename.replace(".md", "")}'
                    })
    return documents

# Make functions available to templates
@app.context_processor
def utility_processor():
    return dict(
        get_markdown_file_list=get_markdown_file_list
    )

# Routes
@app.route("/")
def index():
    courses = get_courses()
    return render_template('landing.html', courses=courses)

@app.route("/docs")
def docs_landing():
    courses = get_courses()
    return render_template('courses.html', courses=courses)

@app.route("/docs/<course>/")
@app.route("/docs/<course>/<path:filename>")
def serve_doc(course, filename=None):
    # Default to welcome.md if filename not provided
    if not filename:
        filename = DEFAULT_DOC

    # Normalize filename
    if not filename.endswith('.md'):
        filename += '.md'

    # Render markdown to HTML
    try:
        html_content = render_markdown_file(course, filename)
    except FileNotFoundError:
        abort(404, f"File {filename} not found in course {course}")

    # Sidebar list
    file_list = get_markdown_file_list(course)

    # Pass to template
    return render_template(
        "docs.html",
        course=course,
        content=html_content,
        files=file_list,
        active_file=filename
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if authenticate_admin(username, password):
            session['admin'] = username
            return redirect(url_for('admin'))
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

@app.route('/admin')
def admin():
    if 'admin' not in session:
        return redirect(url_for('login'))
    
    courses, total_documents = get_courses_with_document_counts()
    total_courses = len(courses)
    
    return render_template('admin.html', 
                         courses=courses, 
                         total_courses=total_courses, 
                         total_documents=total_documents)

# API routes for admin panel
@app.route('/api/courses', methods=['GET'])
def get_courses_api():
    courses = get_courses()
    # Add document counts to each course
    for course in courses:
        course['document_count'] = count_documents_in_course(course['name'])
    return jsonify(courses)

@app.route('/api/courses', methods=['POST'])
def create_course_api():
    if 'admin' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    course_name = data.get('name')
    description = data.get('description', '')
    
    if not course_name:
        return jsonify({'error': 'Course name is required'}), 400
    
    if create_course(course_name, description):
        return jsonify({'message': 'Course created successfully'}), 201
    else:
        return jsonify({'error': 'Course already exists or could not be created'}), 400

@app.route('/api/courses/<course_name>', methods=['DELETE'])
def delete_course_api(course_name):
    if 'admin' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    if delete_course(course_name):
        return jsonify({'message': 'Course deleted successfully'})
    else:
        return jsonify({'error': 'Course not found or could not be deleted'}), 404

@app.route('/api/courses/<course_name>/documents', methods=['GET'])
def get_documents_api(course_name):
    file_list = get_markdown_file_list(course_name)
    documents = []
    for filename in file_list:
        content = get_document_content(course_name, filename)
        documents.append({
            'filename': filename,
            'content': content
        })
    return jsonify(documents)

@app.route('/api/courses/<course_name>/documents', methods=['POST'])
def create_document_api(course_name):
    if 'admin' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    filename = data.get('filename')
    content = data.get('content')
    
    if not filename or not content:
        return jsonify({'error': 'Filename and content are required'}), 400
    
    # Ensure filename ends with .md
    if not filename.endswith('.md'):
        filename += '.md'
    
    if create_document(course_name, filename, content):
        return jsonify({'message': 'Document created successfully'}), 201
    else:
        return jsonify({'error': 'Document could not be created'}), 400

@app.route('/api/courses/<course_name>/documents/<path:filename>', methods=['GET'])
def get_document_api(course_name, filename):
    # Ensure filename ends with .md
    if not filename.endswith('.md'):
        filename += '.md'
        
    content = get_document_content(course_name, filename)
    if content is not None:
        return jsonify({'filename': filename, 'content': content})
    else:
        return jsonify({'error': 'Document not found'}), 404

@app.route('/api/courses/<course_name>/documents/<path:filename>', methods=['PUT'])
def update_document_api(course_name, filename):
    if 'admin' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Ensure filename ends with .md
    if not filename.endswith('.md'):
        filename += '.md'
    
    data = request.get_json()
    content = data.get('content')
    
    if not content:
        return jsonify({'error': 'Content is required'}), 400
    
    if update_document(course_name, filename, content):
        return jsonify({'message': 'Document updated successfully'})
    else:
        return jsonify({'error': 'Document not found or could not be updated'}), 404

@app.route('/api/courses/<course_name>/documents/<path:filename>', methods=['DELETE'])
def delete_document_api(course_name, filename):
    if 'admin' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Ensure filename ends with .md
    if not filename.endswith('.md'):
        filename += '.md'
    
    if delete_document(course_name, filename):
        return jsonify({'message': 'Document deleted successfully'})
    else:
        return jsonify({'error': 'Document not found or could not be deleted'}), 404

@app.route('/api/search')
def search_api():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    results = search_documents(query)
    return jsonify(results)

@app.route('/api/documents')
def all_documents_api():
    documents = get_all_documents()
    return jsonify(documents)

@app.route('/convert-markdown', methods=['POST'])
def convert_markdown():
    data = request.get_json()
    text = data.get('text', '')
    
    # Convert markdown to HTML
    html = md.convert(text)
    
    # Reset markdown parser state
    md.reset()
    
    return html

# Serve media files
@app.route("/media/<path:filename>")
def serve_media(filename):
    return send_file('./media/' + filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
