import re
from typing import Any

def validate_code_format(v: str) -> str:
    """
    Validates that a code field:
    1. Contains no spaces.
    2. Only contains alphanumeric characters, underscores, and dashes.
    3. Is not empty.
    """
    if not v:
        raise ValueError("Code cannot be empty")
    
    if " " in v:
        raise ValueError("Code cannot contain spaces")
    
    if not re.match(r"^[a-zA-Z0-9_-]+$", v):
        raise ValueError("Code can only contain alphanumeric characters, underscores, and dashes")
    
    return v
