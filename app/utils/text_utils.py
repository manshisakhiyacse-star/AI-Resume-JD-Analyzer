import hashlib

def calculate_hash(text: str) -> str:
    """
    Computes the SHA-256 hash of a string to identify duplicate content.
    """
    if not text:
        return ""
    # Normalize whitespace/casing slightly for hash stability
    normalized = " ".join(text.lower().strip().split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
