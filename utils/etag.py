from __future__ import annotations
import hashlib
import json
from typing import Any


def generate_etag(data: Any) -> str:
    """
    Generate an eTag from resource data.
    
    Args:
        data: The resource data (typically a Pydantic model or dict)
    
    Returns:
        A string eTag value (weak eTag format: W/"value")
    """
    # Convert data to a JSON-serializable format if it's a Pydantic model
    if hasattr(data, 'model_dump'):
        serialized = json.dumps(data.model_dump(mode='json'), sort_keys=True)
    elif isinstance(data, dict):
        serialized = json.dumps(data, sort_keys=True)
    else:
        serialized = str(data)
    
    # Generate MD5 hash of the serialized data
    hash_value = hashlib.md5(serialized.encode('utf-8')).hexdigest()
    
    # Return weak eTag format (W/"hash")
    return f'W/"{hash_value}"'


def normalize_etag(etag: str) -> str:
    """
    Normalize eTag by removing quotes and weak prefix for comparison.
    
    Args:
        etag: The eTag string (may be W/"value" or "value")
    
    Returns:
        Normalized eTag value without quotes or weak prefix
    """
    if etag.startswith('W/"'):
        etag = etag[3:-1]
    elif etag.startswith('"'):
        etag = etag[1:-1]
    
    return etag


def etag_match(etag1: str, etag2: str) -> bool:
    """
    Check if two eTags match.
    
    Args:
        etag1: First eTag
        etag2: Second eTag
    
    Returns:
        True if eTags match, False otherwise
    """
    return normalize_etag(etag1) == normalize_etag(etag2)

