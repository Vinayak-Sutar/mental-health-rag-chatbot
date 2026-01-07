"""
Safety Layer
Crisis detection and safety checks.
"""

import re
from typing import Tuple, Optional
import sys
sys.path.insert(0, str(__file__).rsplit('/', 2)[0])

from config.settings import CRISIS_ABORT_KEYWORDS, CRISIS_RESPONSE


class SafetyLayer:
    """Safety checks for mental health chatbot."""
    
    def __init__(self):
        self.crisis_keywords = [kw.lower() for kw in CRISIS_ABORT_KEYWORDS]
        self.crisis_response = CRISIS_RESPONSE
    
    def check_crisis(self, user_input: str) -> Tuple[bool, Optional[str]]:
        """
        Check if user input contains crisis keywords.
        Returns (is_crisis, crisis_response)
        """
        input_lower = user_input.lower()
        
        for keyword in self.crisis_keywords:
            if keyword in input_lower:
                return True, self.crisis_response
        
        return False, None


_safety_layer = None

def get_safety_layer() -> SafetyLayer:
    global _safety_layer
    if _safety_layer is None:
        _safety_layer = SafetyLayer()
    return _safety_layer
