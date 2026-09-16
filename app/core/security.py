import os
import re

def sanitize_filename(filename: str) -> str:
    """
    Sanitizes a filename to prevent path traversal attacks (e.g. ../../etc/passwd)
    and strips any unsafe characters, returning a secure basename.
    """
    if not filename:
        return "uploaded_file"
        
    # Extract only the base name (no directory structure)
    base = os.path.basename(filename)
    
    # Replace any non-alphanumeric, dot, dash, or underscore characters with underscores
    sanitized = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", base)
    
    # Strip leading/trailing dots to prevent hidden files or traversal tricks
    sanitized = sanitized.strip(".")
    
    if not sanitized:
        return "uploaded_file"
        
    return sanitized
