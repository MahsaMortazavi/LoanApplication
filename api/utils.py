import uuid

def generate_uuid(prefix: str) -> str:
    """Generate an opaque ID like '<prefix>_<uuid>'"""
    return f"{prefix}_{uuid.uuid4()}"
