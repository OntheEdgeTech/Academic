from flask import Flask, render_template, send_file, abort, jsonify
import os
import markdown
from flask_caching import Cache

app = Flask(__name__)
app.config['CACHE_TYPE'] = 'simple'  # 'redis' for production
app.config['CACHE_DEFAULT_TIMEOUT'] = 1  # seconds
cache = Cache(app)

# Configuration
DOCS_DIR = os.path.join(os.path.dirname(__file__), 'docs')
DEFAULT_DOC = '1. welcome.md'
COURSE_DOCS_DIR = "docs"
MEDIA_DIR = "media"

def get_markdown_file_list(course_dir):
    """Return a sorted list of markdown files (without extensions) in the course directory."""
    course_path = os.path.join(DOCS_DIR, course_dir)
    if not os.path.exists(course_path):
        return []
    return sorted(
        [f for f in os.listdir(course_path) if f.endswith('.md')],
        key=lambda x: x.lower()
    )

@cache.memoize()
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


@app.route("/")
def index():
    return render_template("landing.html")

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
    html_content = render_markdown_file(course, filename)

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

@app.route("/api/courses")
def get_courses():
    courses = []
    for course_name in os.listdir(COURSE_DOCS_DIR):
        course_path = os.path.join(COURSE_DOCS_DIR, course_name)
        if os.path.isdir(course_path):
            desc_file = os.path.join(course_path, "desc.txt")
            desc = ""
            if os.path.exists(desc_file):
                with open(desc_file, "r") as f:
                    desc = f.read().strip()
                courses.append({
                    "name": course_name,
                    "description": desc,
                    "image": f"/media/{course_name}.png"
                })
    return jsonify(courses)

# Serve media files
@app.route("/media/<path:filename>")
def serve_media(filename):
    return send_file('./media/' + filename)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80)
