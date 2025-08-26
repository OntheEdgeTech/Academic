import json
import os
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
from pathlib import Path

@dataclass
class Course:
    """Course model"""
    id: str
    title: str
    description: str = "No description available"
    instructor: str = "Unknown"
    duration: Optional[str] = None
    level: Optional[str] = None
    docs_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert course to dictionary"""
        return asdict(self)

@dataclass
class Document:
    """Document model"""
    filename: str
    title: str
    content: Optional[str] = None
    toc: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert document to dictionary"""
        return asdict(self)