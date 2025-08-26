import re
import json
import os
from typing import List, Dict
from pathlib import Path
from ..services.course_service import CourseService
from ..utils.helpers import extract_title_from_markdown, sanitize_path
from ..config.settings import Config

class SearchService:
    """Service class for search operations"""
    
    @staticmethod
    def search_documents(query: str) -> List[Dict]:
        """Search for documents containing the query"""
        results = []
        
        if not query or not Config.COURSES_FOLDER.exists():
            return results
        
        # Search across all courses
        for course_dir in Config.COURSES_FOLDER.iterdir():
            if course_dir.is_dir():
                course_docs_path = course_dir / 'docs'
                if course_docs_path.exists():
                    for file_path in course_docs_path.iterdir():
                        if file_path.suffix == '.md':
                            try:
                                content = file_path.read_text(encoding='utf-8')
                                
                                # Check if query is in content (case insensitive)
                                if re.search(query, content, re.IGNORECASE):
                                    # Extract title
                                    title = extract_title_from_markdown(content, file_path.name)
                                    
                                    # Get course info
                                    course_title = SearchService._get_course_title(course_dir.name)
                                    
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
                                        'course_id': course_dir.name,
                                        'filename': file_path.name,
                                        'title': title,
                                        'course_title': course_title,
                                        'snippet': snippet
                                    })
                            except Exception:
                                continue
        
        return results
    
    @staticmethod
    def _get_course_title(course_id: str) -> str:
        """Get course title from course info or format course ID"""
        if not sanitize_path(course_id):
            return course_id
            
        course_info_path = Config.COURSES_FOLDER / course_id / 'course.json'
        course_title = course_id.replace('_', ' ').replace('-', ' ').title()
        
        if course_info_path.exists():
            try:
                with open(course_info_path, 'r') as f:
                    course_data = json.load(f)
                    course_title = course_data.get('title', course_title)
            except:
                pass
        
        return course_title