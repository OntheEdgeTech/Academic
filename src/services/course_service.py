import os
import json
import markdown
from typing import List, Tuple, Optional, Dict
from pathlib import Path
from ..models.course_models import Course, Document
from ..utils.helpers import format_title, extract_title_from_markdown, sanitize_path
from ..config.settings import Config
from .. import cache

class CourseService:
    """Service class for course-related operations"""
    
    @staticmethod
    @cache.cached(timeout=300, key_prefix='all_courses')
    def get_all_courses() -> List[Course]:
        """Get list of all courses"""
        courses = []
        if Config.COURSES_FOLDER.exists():
            for course_dir in Config.COURSES_FOLDER.iterdir():
                if course_dir.is_dir():
                    course = CourseService._load_course_info(course_dir.name)
                    course.docs_count = CourseService._count_course_documents(course_dir.name)
                    courses.append(course)
        
        return sorted(courses, key=lambda x: x.title)
    
    @staticmethod
    @cache.memoize(timeout=300)
    def get_course_documents(course_id: str) -> List[Document]:
        """Get list of documents for a specific course"""
        if not sanitize_path(course_id):
            return []
            
        docs = []
        course_docs_path = Config.COURSES_FOLDER / course_id / 'docs'
        
        if course_docs_path.exists():
            for file_path in course_docs_path.iterdir():
                if file_path.suffix == '.md':
                    title = format_title(file_path.stem)
                    docs.append(Document(
                        filename=file_path.name,
                        title=title
                    ))
        
        return sorted(docs, key=lambda x: x.title)
    
    @staticmethod
    @cache.memoize(timeout=300)
    def read_course_document(course_id: str, filename: str) -> Tuple[Optional[Document], Optional[str]]:
        """Read and parse markdown document from a course"""
        if not sanitize_path(course_id) or not sanitize_path(filename):
            return None, "Invalid path"
            
        filepath = Config.COURSES_FOLDER / course_id / 'docs' / filename
        if not filepath.exists():
            return None, "Document not found"
        
        try:
            content = filepath.read_text(encoding='utf-8')
            
            all_builtin = [
                'abbr', 'attr_list', 'def_list', 'fenced_code', 'footnotes', 'md_in_html',
                'tables', 'admonition', 'codehilite', 'legacy_attrs', 'legacy_em',
                'meta', 'nl2br', 'sane_lists', 'smarty', 'toc', 'wikilinks'
            ]

            # Convert markdown to HTML
            md = markdown.Markdown(extensions=all_builtin)
            html_content = md.convert(content)
            
            # Extract title
            title = extract_title_from_markdown(content, filename)
            
            document = Document(
                filename=filename,
                title=title,
                content=html_content,
                toc=getattr(md, 'toc', '')
            )
            
            return document, None
        except Exception as e:
            return None, f"Error reading document: {str(e)}"
    
    @staticmethod
    def save_course_info(course_id: str, course_data: Dict) -> bool:
        """Save course information to course.json"""
        if not sanitize_path(course_id):
            return False
            
        course_path = Config.COURSES_FOLDER / course_id
        course_path.mkdir(exist_ok=True)
        
        course_info_path = course_path / 'course.json'
        try:
            with open(course_info_path, 'w') as f:
                json.dump(course_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving course info: {e}")
            return False
    
    @staticmethod
    def save_document(course_id: str, filename: str, content: str) -> bool:
        """Save a document to a course"""
        if not sanitize_path(course_id) or not sanitize_path(filename):
            return False
            
        course_docs_path = Config.COURSES_FOLDER / course_id / 'docs'
        course_docs_path.mkdir(exist_ok=True)
        
        filepath = course_docs_path / filename
        try:
            filepath.write_text(content, encoding='utf-8')
            return True
        except Exception as e:
            print(f"Error saving document: {e}")
            return False
    
    @staticmethod
    def delete_document(course_id: str, filename: str) -> bool:
        """Delete a document from a course"""
        if not sanitize_path(course_id) or not sanitize_path(filename):
            return False
            
        filepath = Config.COURSES_FOLDER / course_id / 'docs' / filename
        if filepath.exists():
            try:
                filepath.unlink()
                return True
            except Exception as e:
                print(f"Error deleting document: {e}")
                return False
        return False
    
    @staticmethod
    @cache.memoize(timeout=300)
    def _load_course_info(course_id: str) -> Course:
        """Load course information from course.json or create default"""
        if not sanitize_path(course_id):
            return Course(id=course_id, title=format_title(course_id))
            
        course_info_path = Config.COURSES_FOLDER / course_id / 'course.json'
        course_info = Course(
            id=course_id,
            title=format_title(course_id),
            description='No description available',
            instructor='Unknown'
        )
        
        if course_info_path.exists():
            try:
                with open(course_info_path, 'r') as f:
                    course_data = json.load(f)
                    # Update course info with loaded data
                    for key, value in course_data.items():
                        if hasattr(course_info, key):
                            setattr(course_info, key, value)
            except:
                pass
        
        return course_info
    
    @staticmethod
    @cache.memoize(timeout=300)
    def _count_course_documents(course_id: str) -> int:
        """Count documents in a course"""
        if not sanitize_path(course_id):
            return 0
            
        docs_count = 0
        course_docs_path = Config.COURSES_FOLDER / course_id / 'docs'
        
        if course_docs_path.exists():
            for file_path in course_docs_path.iterdir():
                if file_path.suffix == '.md':
                    docs_count += 1
        
        return docs_count