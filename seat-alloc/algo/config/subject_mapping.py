"""
Subject Code → Name Mapping
============================
Hardcoded mapping of subject codes to full subject names.
Used by the debarred attendance export to resolve subject names
when teachers only provide subject codes in their debarred lists.

Easily extensible — just add new entries to SUBJECT_CODE_MAP.
"""

# ── Subject Code → Name ────────────────────────────────────────────────────
SUBJECT_CODE_MAP = {
    # CS (Computer Science & Engineering) — prefix 1525
    '15251201': 'Computer Graphics',
    '15251202': 'Object Oriented Program and Methodology',
    '15251203': 'Computer System & Organisation',
    '15251204': 'Operating Systems',
    '15251205': 'Basic Electrical & Electronics Engineering',

    # CSD (Computer Science & Design) — prefix 2925
    '29251201': 'Computer Graphics & Animation',
    '29251202': 'Object Oriented Programming & Methodology',
    '29251203': 'CSO',
    '29251204': 'Operating Systems',
    '29251205': 'Basic Electrical & Electronics Engineering',
}


def resolve_subject_name(code: str) -> str:
    """
    Look up the full subject name for a given subject code.

    Args:
        code: Subject code string (e.g. '15251201')

    Returns:
        The resolved subject name, or the original code if not found.
    """
    return SUBJECT_CODE_MAP.get(code.strip(), code)
