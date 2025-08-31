import json
import os
from dataclasses import dataclass, asdict
from typing import Dict, List
from pathlib import Path
from ..config.settings import Config

@dataclass
class CourseLike:
    """Model for course likes"""
    course_id: str
    like_count: int = 0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)