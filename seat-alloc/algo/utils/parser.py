# Advanced student data parser for Excel and CSV files.
# Handles format detection, column mapping, and data normalization for student enrollments.
from __future__ import annotations

import io
import uuid
import re
import json
import logging
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union, Optional

import pandas as pd

logger = logging.getLogger("student_parser")
logger.setLevel(logging.INFO)

# ============================================================================
# COLOR PALETTE FOR BATCH GENERATION
# High-contrast, easily distinguishable light colors
# ============================================================================
BATCH_COLORS = [
    '#93C5FD',  # Blue (distinct)
    '#FCA5A5',  # Red (distinct)
    '#86EFAC',  # Green (distinct)
    '#FCD34D',  # Amber/Yellow (warm)
    '#C4B5FD',  # Purple (distinct)
    '#F9A8D4',  # Pink (distinct)
    '#67E8F9',  # Cyan (cool)
    '#FDBA74',  # Orange (warm, distinct from amber)
    '#5EEAD4',  # Teal (cool, distinct from cyan)
    '#A78BFA',  # Violet (deeper, distinct from purple)
    '#FEF08A',  # Light Yellow (bright)
    '#6EE7B7',  # Emerald (distinct from green)
]

def _norm_col_name(x: Any) -> str:
    """Normalize column header: lowercase, no spaces/punct, alnum only."""
    if x is None:
        return ""
    s = str(x).strip().lower()
    s = re.sub(r"[^0-9a-z]", "", s)
    return s

def _normalize_enrollment_value(v: Any) -> str:
    """Normalize an enrollment value: strip, remove internal whitespace."""
    if v is None:
        return ""
    s = str(v).strip()
    s = re.sub(r"\s+", "", s)
    return s

def _generate_batch_color() -> str:
    """Generate a random batch color from predefined palette."""
    return random.choice(BATCH_COLORS)


def _get_color_for_batch_name(batch_name: str) -> str:
    """
    Generate a deterministic color based on batch name.
    Different batch names will get different colors (hash-based).
    """
    # Use hash of batch name to pick color index
    hash_value = hash(batch_name.strip().upper())
    color_index = abs(hash_value) % len(BATCH_COLORS)
    return BATCH_COLORS[color_index]

# ============================================================================
# PARSE RESULT DATACLASS (ENHANCED)
# ============================================================================
@dataclass
class ParseResult:
    """
    Result of parsing a student data file.
    
    NEW: batch_color attribute for UI rendering
    """
    batch_id: str
    batch_name: str
    batch_color: str  # NEW: Color hex code for this batch
    mode: int
    source_filename: Optional[str]
    rows_total: int
    rows_extracted: int
    warnings: List[Dict] = field(default_factory=list)
    errors: List[Dict] = field(default_factory=list)
    data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'batch_id': self.batch_id,
            'batch_name': self.batch_name,
            'batch_color': self.batch_color,
            'mode': self.mode,
            'source_filename': self.source_filename,
            'rows_total': self.rows_total,
            'rows_extracted': self.rows_extracted,
            'warnings': self.warnings,
            'errors': self.errors,
            'data': self.data
        }

# ============================================================================
# STUDENT DATA PARSER (ENHANCED)
# ============================================================================
class StudentDataParser:
    """
    Production-grade parser for student enrollment data.
    
    Supports CSV and Excel formats with automatic column detection.
    """
    
    def __init__(
        self,
        enrollment_regex: str = r"^[A-Za-z0-9\-\_/]+$",
        supported_formats: Optional[List[str]] = None,
    ) -> None:
        """
        Initialize parser with validation rules.
        
        Args:
            enrollment_regex: Pattern for valid enrollment numbers
            supported_formats: List of allowed file extensions
        """
        self.enrollment_pattern = re.compile(enrollment_regex)
        self.supported_formats = supported_formats or [".csv", ".xlsx", ".xls"]
        self.last_parse_result: Optional[ParseResult] = None

    # ========================================================================
    # FILE READING WITH FORMAT DETECTION
    # ========================================================================
    
    def read_file(self, file_input: Union[str, bytes, io.BytesIO, Any]) -> pd.DataFrame:
        """
        Read a CSV/XLSX into a pandas DataFrame (dtype=str, keep_default_na=False).

        Supports:
        - Path string
        - bytes
        - file-like (has .read())
        
        Returns:
            DataFrame with all columns as strings, no NaN values
        """
        # Path string case
        if isinstance(file_input, str):
            p = Path(file_input)
            suffix = p.suffix.lower()
            if suffix not in self.supported_formats:
                raise ValueError(f"Unsupported file extension: {suffix}. Supported: {self.supported_formats}")

            if suffix == ".csv":
                # Try several encodings
                for enc in ("utf-8", "latin-1", "iso-8859-1", "cp1252"):
                    try:
                        df = pd.read_csv(
                            file_input, 
                            dtype=str, 
                            keep_default_na=False, 
                            encoding=enc
                        )
                        logger.info(f"Successfully read CSV with {enc} encoding")
                        return df
                    except UnicodeDecodeError:
                        continue
                    except Exception as e:
                        logger.warning(f"Failed to read CSV with {enc}: {e}")
                        continue
                raise ValueError("Failed to read CSV with any common encoding (utf-8, latin-1, iso-8859-1, cp1252)")
            else:
                # Excel
                try:
                    return pd.read_excel(file_input, dtype=str, keep_default_na=False)
                except Exception as e:
                    raise ValueError(f"Failed to read Excel file: {str(e)}")

        # Bytes case
        if isinstance(file_input, (bytes, bytearray)):
            head = bytes(file_input[:8]) if len(file_input) >= 8 else b""
            
            # XLSX = zip = PK\x03\x04
            if head.startswith(b"PK\x03\x04"):
                try:
                    df = pd.read_excel(
                        io.BytesIO(file_input), dtype=str, keep_default_na=False
                    )
                    logger.info("Detected and read XLSX format")
                    return df
                except Exception as e:
                    raise ValueError(f"Failed to read XLSX from bytes: {str(e)}")
            
            # Old XLS = D0 CF 11 E0 (compound file)
            if head.startswith(b"\xD0\xCF\x11\xE0"):
                try:
                    df = pd.read_excel(
                        io.BytesIO(file_input), dtype=str, keep_default_na=False
                    )
                    logger.info("Detected and read XLS format")
                    return df
                except Exception as e:
                    raise ValueError(f"Failed to read XLS from bytes: {str(e)}")
            
            # Fallback: treat as CSV
            for enc in ("utf-8", "latin-1", "cp1252"):
                try:
                    text = file_input.decode(enc)
                    df = pd.read_csv(
                        io.StringIO(text), dtype=str, keep_default_na=False
                    )
                    logger.info(f"Treated as CSV with {enc} encoding")
                    return df
                except Exception:
                    continue
            raise ValueError("Unable to parse bytes as CSV or Excel. Check file format.")

        # File-like (e.g., Flask FileStorage, UploadFile.stream)
        if hasattr(file_input, "read"):
            # Save current position
            try:
                pos = file_input.tell()
            except Exception:
                pos = None

            # Read first 8 bytes for magic number detection
            head = file_input.read(8)
            
            # Restore position
            try:
                if pos is not None:
                    file_input.seek(pos)
                else:
                    file_input.seek(0)
            except Exception:
                pass

            # Detect format from magic bytes
            if isinstance(head, (bytes, bytearray)):
                # Excel formats
                if head.startswith(b"PK\x03\x04") or head.startswith(b"\xD0\xCF\x11\xE0"):
                    try:
                        content = file_input.read()
                        if not isinstance(content, (bytes, bytearray)):
                            content = str(content).encode("utf-8")
                        df = pd.read_excel(
                            io.BytesIO(content), dtype=str, keep_default_na=False
                        )
                        logger.info("Detected Excel format from file-like object")
                        return df
                    except Exception as e:
                        try:
                            file_input.seek(0)
                        except Exception:
                            pass
                        raise ValueError(f"Failed to read Excel from upload: {str(e)}")

                # CSV format
                content = file_input.read()
                try:
                    file_input.seek(0)
                except Exception:
                    pass
                
                if isinstance(content, (bytes, bytearray)):
                    for enc in ("utf-8", "latin-1", "cp1252"):
                        try:
                            text = content.decode(enc)
                            df = pd.read_csv(
                                io.StringIO(text),
                                dtype=str,
                                keep_default_na=False,
                            )
                            logger.info(f"Read CSV from file-like with {enc}")
                            return df
                        except Exception:
                            continue
                else:
                    # Already text
                    df = pd.read_csv(
                        io.StringIO(str(content)), dtype=str, keep_default_na=False
                    )
                    logger.info("Read CSV from text content")
                    return df

                # Final fallback: try Excel
                try:
                    file_input.seek(0)
                    df = pd.read_excel(file_input, dtype=str, keep_default_na=False)
                    logger.info("Fallback Excel read succeeded")
                    return df
                except Exception:
                    pass

            # Head is text (shouldn't happen but handle it)
            content = file_input.read()
            try:
                file_input.seek(0)
            except Exception:
                pass
            return pd.read_csv(
                io.StringIO(str(head) + str(content)),
                dtype=str,
                keep_default_na=False,
            )

        raise ValueError(f"Unsupported input type for read_file: {type(file_input)}")

    # ========================================================================
    # COLUMN DETECTION
    # ========================================================================
    
    def detect_columns(self, df: pd.DataFrame) -> Dict[str, Optional[str]]:
        """
        Auto-detect likely 'name', 'enrollment', and 'department' columns.
        
        Returns:
            {'name': original_col_or_None, 'enrollment': original_col_or_None, 'department': ...}
        """
        detected = {"name": None, "enrollment": None, "department": None}
        norm_map: Dict[str, str] = {}
        
        for c in df.columns:
            norm_map[_norm_col_name(c)] = c

        # Column keywords (prioritized)
        enroll_keys = [
            "enrollment", "enrollmentno", "enroll", "enrollno", "enrollmentnumber",
            "roll", "rollno", "regno", "registrationno", "registration",
            "studentid", "id", "matricno", "matric"
        ]
        
        name_keys = [
            "name", "studentname", "fullname", "candidate", 
            "firstname", "fname", "student"
        ]
        
        dept_keys = [
            "department", "dept", "branch", "course", 
            "program", "stream", "discipline"
        ]

        # Exact normalized key match (highest priority)
        for key in enroll_keys:
            if key in norm_map:
                detected["enrollment"] = norm_map[key]
                break
        
        for key in name_keys:
            if key in norm_map:
                detected["name"] = norm_map[key]
                break
        
        for key in dept_keys:
            if key in norm_map:
                detected["department"] = norm_map[key]
                break

        # Fallback: substring match
        if detected["enrollment"] is None:
            for norm, orig in norm_map.items():
                if any(k in norm for k in enroll_keys):
                    detected["enrollment"] = orig
                    logger.info(f"Detected enrollment column via substring: {orig}")
                    break

        if detected["name"] is None:
            for norm, orig in norm_map.items():
                if any(k in norm for k in name_keys):
                    detected["name"] = orig
                    logger.info(f"Detected name column via substring: {orig}")
                    break
        
        if detected["department"] is None:
            for norm, orig in norm_map.items():
                if any(k in norm for k in dept_keys):
                    detected["department"] = orig
                    logger.info(f"Detected department column via substring: {orig}")
                    break

        return detected

    # ========================================================================
    # EXTRACTION MODES
    # ========================================================================
    
    def extract_mode1(
        self, df: pd.DataFrame, enrollment_col: Optional[str] = None
    ) -> Tuple[List[str], List[Dict]]:
        """
        Mode 1: extract only enrollment numbers.
        
        Returns:
            (enrollments_list, warnings_list)
        """
        warnings: List[Dict] = []
        detected = self.detect_columns(df)
        
        if enrollment_col is None:
            enrollment_col = detected.get("enrollment")

        if enrollment_col is None or enrollment_col not in df.columns:
            raise ValueError(
                f"Enrollment column not found. Available columns: {df.columns.tolist()}"
            )

        enrollments: List[str] = []
        for idx, value in enumerate(df[enrollment_col].tolist(), start=2):  # Row 2 = first data row
            if value is None or value == "" or (isinstance(value, float) and pd.isna(value)):
                warnings.append({
                    "row": idx, 
                    "issue": "empty_enrollment", 
                    "value": None,
                    "message": f"Row {idx}: Empty enrollment number"
                })
                continue
            
            norm = _normalize_enrollment_value(value)
            if not norm:
                warnings.append({
                    "row": idx,
                    "issue": "empty_after_normalization",
                    "value": value,
                    "message": f"Row {idx}: Enrollment became empty after normalization"
                })
                continue
            
            if not self.enrollment_pattern.match(norm):
                warnings.append({
                    "row": idx,
                    "issue": "invalid_enrollment_format",
                    "value": value,
                    "normalized": norm,
                    "message": f"Row {idx}: Enrollment '{value}' has invalid format"
                })
                # Still include it (lenient mode)
            
            enrollments.append(norm)
        
        return enrollments, warnings

    def extract_mode2(
        self,
        df: pd.DataFrame,
        name_col: Optional[str] = None,
        enrollment_col: Optional[str] = None,
    ) -> Tuple[List[Dict[str, str]], List[Dict]]:
        """
        Mode 2: extract name + enrollment + department.
        
        Returns:
            (students_list, warnings_list)
            students_list entry: {'name': ..., 'enrollmentNo': ..., 'department': ...}
        """
        warnings: List[Dict] = []
        detected = self.detect_columns(df)
        
        if enrollment_col is None:
            enrollment_col = detected.get("enrollment")
        if name_col is None:
            name_col = detected.get("name")
        
        dept_col = detected.get("department")

        # Enrollment column is REQUIRED
        if enrollment_col is None or enrollment_col not in df.columns:
            raise ValueError(
                f"Enrollment column not found. Available columns: {df.columns.tolist()}"
            )
        
        # Name column is OPTIONAL (warning if missing)
        if name_col is None or name_col not in df.columns:
            warnings.append({
                "issue": "name_column_not_found",
                "available_columns": df.columns.tolist(),
                "message": "Name column not detected - names will be empty"
            })
            name_col = None

        students: List[Dict[str, str]] = []
        for idx, row in enumerate(df.to_dict(orient="records"), start=2):  # Row 2 = first data row
            raw_en = row.get(enrollment_col)
            
            # Skip empty enrollments
            if raw_en is None or raw_en == "":
                warnings.append({
                    "row": idx, 
                    "issue": "empty_enrollment", 
                    "value": None,
                    "message": f"Row {idx}: Empty enrollment - skipping"
                })
                continue
            
            enroll_norm = _normalize_enrollment_value(raw_en)
            if not enroll_norm:
                warnings.append({
                    "row": idx,
                    "issue": "empty_after_normalization",
                    "value": raw_en,
                    "message": f"Row {idx}: Enrollment became empty after cleanup"
                })
                continue
            
            # Validate format
            if not self.enrollment_pattern.match(enroll_norm):
                warnings.append({
                    "row": idx,
                    "issue": "invalid_enrollment_format",
                    "value": raw_en,
                    "normalized": enroll_norm,
                    "message": f"Row {idx}: Enrollment format validation failed"
                })
            
            # Extract name
            name_val = ""
            if name_col:
                nv = row.get(name_col)
                name_val = "" if nv is None else str(nv).strip()
            
            # Extract department
            dept_val = ""
            if dept_col:
                dv = row.get(dept_col)
                dept_val = "" if dv is None else str(dv).strip()
            
            students.append({
                "name": name_val, 
                "enrollmentNo": enroll_norm,
                "department": dept_val
            })
        
        return students, warnings

    # ========================================================================
    # PUBLIC PARSE API
    # ========================================================================
    
    def parse_file(
        self,
        file_input: Union[str, bytes, io.BytesIO, Any],
        mode: int = 2,
        batch_name: str = "BATCH1",
        name_col: Optional[str] = None,
        enrollment_col: Optional[str] = None,
        batch_color: Optional[str] = None,
    ) -> ParseResult:
        """
        Main parse entrypoint.
        
        Args:
            file_input: File path, bytes, or file-like object
            mode: 1 (enrollment only) or 2 (name + enrollment)
            batch_name: Label for this batch
            name_col: Override name column detection
            enrollment_col: Override enrollment column detection
            batch_color: Override color (otherwise auto-generated)
        
        Returns:
            ParseResult with data formatted as:
                mode=1 -> {"BATCH1": ["E1","E2",...]}
                mode=2 -> {"BATCH1": [{"name":..,"enrollmentNo":..,"department":...}, ...]}
        """
        logger.info(f"Starting parse: mode={mode}, batch={batch_name}")
        
        # Read file
        try:
            df = self.read_file(file_input)
        except Exception as e:
            logger.error(f"File read failed: {e}")
            raise ValueError(f"Failed to read file: {str(e)}")
        
        # Determine source filename
        source_filename = None
        if isinstance(file_input, str):
            source_filename = Path(file_input).name
        elif hasattr(file_input, "filename"):
            source_filename = getattr(file_input, "filename")
        elif hasattr(file_input, "name"):
            source_filename = getattr(file_input, "name")

        rows_total = len(df)
        logger.info(f"Read {rows_total} rows from {source_filename or 'uploaded file'}")
        
        # Generate color based on batch name (deterministic - same name = same color)
        if batch_color is None:
            batch_color = _get_color_for_batch_name(batch_name)
        
        warnings: List[Dict] = []

        # Extract based on mode
        if mode == 1:
            extracted, warnings = self.extract_mode1(df, enrollment_col)
            formatted = {batch_name: extracted}
        elif mode == 2:
            extracted, warnings = self.extract_mode2(df, name_col, enrollment_col)
            formatted = {batch_name: extracted}
        else:
            raise ValueError(f"Invalid mode: {mode}. Must be 1 or 2.")

        # Create result
        pr = ParseResult(
            batch_id=str(uuid.uuid4()),
            batch_name=batch_name,
            batch_color=batch_color,
            mode=mode,
            source_filename=source_filename,
            rows_total=rows_total,
            rows_extracted=len(formatted[batch_name]),
            warnings=warnings,
            errors=[],
            data=formatted,
        )
        
        self.last_parse_result = pr
        
        logger.info(f"Parse complete: {pr.rows_extracted}/{pr.rows_total} records extracted, {len(warnings)} warnings")
        
        return pr

    # ========================================================================
    # PREVIEW
    # ========================================================================
    
    def preview(
        self, file_input: Union[str, bytes, io.BytesIO, Any], max_rows: int = 5
    ) -> Dict[str, Any]:
        """
        Quick preview of file structure without full parsing.
        
        Args:
            file_input: File to preview
            max_rows: Number of sample rows to return
        
        Returns:
            Dictionary with columns, detected columns, sample data, and row count
        """
        try:
            df = self.read_file(file_input)
        except Exception as e:
            return {
                "error": str(e),
                "columns": [],
                "detectedColumns": {},
                "sampleData": [],
                "totalRows": 0
            }
        
        detected = self.detect_columns(df)
        sample = df.head(max_rows).fillna("").to_dict(orient="records")
        
        return {
            "columns": list(map(str, df.columns.tolist())),
            "detectedColumns": detected,
            "sampleData": sample,
            "totalRows": len(df),
        }

    # ========================================================================
    # JSON HELPERS
    # ========================================================================
    
    def to_json_str(self, parse_result: Optional[ParseResult] = None) -> str:
        """Serialize ParseResult to JSON string."""
        if parse_result is None:
            parse_result = self.last_parse_result
        if parse_result is None:
            raise ValueError("No parse result available")
        
        return json.dumps(parse_result.to_dict(), ensure_ascii=False, indent=2)

    def to_json_file(self, path: str, parse_result: Optional[ParseResult] = None) -> None:
        """Save ParseResult to JSON file."""
        s = self.to_json_str(parse_result)
        Path(path).write_text(s, encoding="utf-8")
