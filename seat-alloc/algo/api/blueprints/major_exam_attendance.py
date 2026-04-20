"""
Major Exam Attendance & Master Plan PDF Blueprint
"""
from flask import Blueprint, request, jsonify, send_file
import io
import os
import logging
from pathlib import Path
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak

from algo.services.auth_service import token_required
from algo.core.cache.major_exam_cache import get_major_cache_manager
from algo.core.cache.major_exam_template_manager import MajorExamTemplateManager

major_exam_attendance_bp = Blueprint('major_exam_attendance', __name__, url_prefix='/api/major-exam')
cache_manager = get_major_cache_manager()
template_manager = MajorExamTemplateManager()
logger = logging.getLogger(__name__)

_BASE_DIR = Path(__file__).resolve().parent.parent.parent
BANNER_PATH = str(_BASE_DIR / 'pdf_gen' / 'data' / 'banner.png')


DEPARTMENT_CODE_MAP = {
    'CSE': 'Computer Science and Engineering',
    'CSD': 'Computer Science and Design',
    'CSM': 'Computer Science and Mathematics',
    'ECE': 'Electronics and Communication Engineering',
    'EEE': 'Electrical and Electronics Engineering',
    'ME': 'Mechanical Engineering',
    'CE': 'Civil Engineering',
    'IT': 'Information Technology',
}


def get_banner_image():
    """Load banner image if available."""
    if os.path.exists(BANNER_PATH):
        try:
            return Image(BANNER_PATH, width=18.6 * cm, height=3 * cm, kind='proportional')
        except Exception:
            return None
    return None


def _safe_int(value, default=0):
    """Best-effort int conversion."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _department_heading(value: str):
    """Normalize department headings from short codes or raw text."""
    raw = str(value or '').strip()
    if not raw:
        return 'Department of Computer Science and Engineering'

    if raw.lower().startswith('department of '):
        return raw

    upper = raw.upper()
    if upper in DEPARTMENT_CODE_MAP:
        return f"Department of {DEPARTMENT_CODE_MAP[upper]}"

    return f"Department of {raw}"


def _roll_range(students):
    """Compute from/to enrollment range from students."""
    enrollments = [str(s.get('enrollment', '')).strip() for s in students if s.get('enrollment')]
    enrollments = [e for e in enrollments if e]
    if not enrollments:
        return '', ''
    enrollments.sort()
    return enrollments[0], enrollments[-1]


def _normalize_branch_allocations(room_data: dict):
    """Normalize branch allocation shape from new or legacy room payloads."""
    normalized = {}

    # New shape: room.branch_allocations[branch] -> {students, count, from_roll, to_roll}
    raw_allocs = room_data.get('branch_allocations', {})
    if isinstance(raw_allocs, dict) and raw_allocs:
        for branch_name, alloc in raw_allocs.items():
            if not isinstance(alloc, dict):
                continue
            students = alloc.get('students', [])
            students = students if isinstance(students, list) else []
            from_roll = alloc.get('from_roll', '')
            to_roll = alloc.get('to_roll', '')
            if not from_roll or not to_roll:
                calc_from, calc_to = _roll_range(students)
                from_roll = from_roll or calc_from
                to_roll = to_roll or calc_to
            normalized[branch_name] = {
                'students': students,
                'count': _safe_int(alloc.get('count'), len(students)),
                'from_roll': from_roll,
                'to_roll': to_roll,
            }
        if normalized:
            return normalized

    # Legacy shape: room.batches[batch] -> {info, students, from_roll, to_roll, total}
    batches = room_data.get('batches', {})
    if isinstance(batches, dict):
        for batch_name, batch_data in batches.items():
            if not isinstance(batch_data, dict):
                continue
            students = batch_data.get('students', [])
            students = students if isinstance(students, list) else []
            info = batch_data.get('info', {}) if isinstance(batch_data.get('info', {}), dict) else {}
            branch_name = info.get('branch') or batch_name
            from_roll = batch_data.get('from_roll', '')
            to_roll = batch_data.get('to_roll', '')
            if not from_roll or not to_roll:
                calc_from, calc_to = _roll_range(students)
                from_roll = from_roll or calc_from
                to_roll = to_roll or calc_to
            normalized[branch_name] = {
                'students': students,
                'count': _safe_int(batch_data.get('count') or batch_data.get('total'), len(students)),
                'from_roll': from_roll,
                'to_roll': to_roll,
            }

    return normalized


def _normalize_single_room(room_data: dict, fallback_name: str = ''):
    """Normalize one room record to the current room schema."""
    room_name = room_data.get('room_name') or room_data.get('name') or fallback_name
    branch_allocations = _normalize_branch_allocations(room_data)
    total_students = room_data.get('total_students')
    if total_students is None:
        total_students = room_data.get('allocated_count')
    if total_students is None:
        total_students = sum(v.get('count', 0) for v in branch_allocations.values())

    return {
        'room_name': room_name,
        'capacity': _safe_int(room_data.get('capacity'), 0),
        'total_students': _safe_int(total_students, 0),
        'branch_allocations': branch_allocations,
    }


def _normalize_rooms(plan_data: dict):
    """Normalize plan rooms to list[{room_name, capacity, total_students, branch_allocations}]."""
    rooms = plan_data.get('rooms', [])
    normalized = []

    if isinstance(rooms, list):
        for room in rooms:
            if isinstance(room, dict):
                normalized.append(_normalize_single_room(room))
        return normalized

    # Legacy dictionary keyed by room name
    if isinstance(rooms, dict):
        for room_name, room_data in rooms.items():
            if isinstance(room_data, dict):
                normalized.append(_normalize_single_room(room_data, fallback_name=room_name))

    return normalized


def _flatten_students_from_plan(plan_data: dict):
    """Flatten all students from plan shape (rooms/branches/students)."""
    students = []

    # Current + legacy room-aware shape
    rooms = _normalize_rooms(plan_data)
    if rooms:
        for room in rooms:
            branch_allocs = room.get('branch_allocations', {})
            for branch_name, alloc in branch_allocs.items():
                for student in alloc.get('students', []):
                    enriched = dict(student)
                    enriched['room_name'] = room.get('room_name', '')
                    enriched['branch'] = enriched.get('branch') or branch_name
                    students.append(enriched)
        return students

    # Branch-map shape
    branches = plan_data.get('branches', {})
    if isinstance(branches, dict) and branches:
        for branch_name, branch_students in branches.items():
            for student in branch_students:
                enriched = dict(student)
                enriched['branch'] = enriched.get('branch') or branch_name
                students.append(enriched)
        return students

    # Legacy flat shape
    legacy_students = plan_data.get('students', [])
    if isinstance(legacy_students, list):
        return [dict(s) for s in legacy_students]

    return []


def _select_students(plan_data: dict, room_name: str = None, branch_filter: str = None):
    """Select students optionally filtered by room and branch."""
    rooms = _normalize_rooms(plan_data)
    selected = []

    if rooms:
        for room in rooms:
            current_room = room.get('room_name', '')
            if room_name and current_room != room_name:
                continue

            branch_allocs = room.get('branch_allocations', {})
            for branch_name, alloc in branch_allocs.items():
                if branch_filter and branch_name != branch_filter:
                    continue

                for student in alloc.get('students', []):
                    enriched = dict(student)
                    enriched['room_name'] = current_room
                    enriched['branch'] = enriched.get('branch') or branch_name
                    selected.append(enriched)
    else:
        selected = _flatten_students_from_plan(plan_data)
        if branch_filter:
            selected = [s for s in selected if s.get('branch') == branch_filter]

    selected.sort(key=lambda s: str(s.get('enrollment', '')))
    return selected


def _attendance_metadata(plan_data: dict, template_data: dict):
    """Merge attendance metadata with safe defaults."""
    raw = plan_data.get('attendance_metadata', {})
    department_raw = raw.get('department') or template_data.get('major_exam_dept_name', 'Computer Science and Engineering')
    return {
        'exam_name': raw.get('exam_name') or template_data.get('major_exam_heading', 'MAJOR EXAMINATION'),
        'department': _department_heading(department_raw),
        'course_name': raw.get('course_name') or plan_data.get('course_name', ''),
        'course_code': raw.get('course_code') or plan_data.get('course_code', ''),
        'exam_date': raw.get('exam_date') or plan_data.get('date', ''),
        'notes': raw.get('notes', ''),
        'invigilator_1': raw.get('invigilator_1', ''),
        'invigilator_2': raw.get('invigilator_2', ''),
        'invigilator_3': raw.get('invigilator_3', ''),
    }


def _master_metadata(plan_data: dict, template_data: dict):
    """Master-plan-specific metadata with fallback to attendance metadata."""
    attendance = _attendance_metadata(plan_data, template_data)
    raw = plan_data.get('master_metadata', {})
    return {
        'exam_name': raw.get('exam_name') or attendance['exam_name'],
        'department': _department_heading(raw.get('department') or attendance['department']),
        'course_name': raw.get('course_name') or attendance['course_name'],
        'course_code': raw.get('course_code') or attendance['course_code'],
        'exam_date': raw.get('exam_date') or attendance['exam_date'] or datetime.now().strftime('%d.%m.%Y'),
        'invigilator_1': raw.get('invigilator_1') or attendance['invigilator_1'],
        'invigilator_2': raw.get('invigilator_2') or attendance['invigilator_2'],
        'invigilator_3': raw.get('invigilator_3') or attendance['invigilator_3'],
    }


def generate_attendance_pdf(plan_data: dict, room_name: str = None, branch_filter: str = None,
                            template_data: dict = None, user_id: str = None) -> bytes:
    """Generate room/branch-aware attendance PDF with Times styling."""
    try:
        if template_data is None and user_id:
            template_data = template_manager.get_user_template(user_id)
        if template_data is None:
            template_data = {}

        students = _select_students(plan_data, room_name=room_name, branch_filter=branch_filter)
        if not students:
            return None

        meta = _attendance_metadata(plan_data, template_data)

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            topMargin=1.2 * cm,
            bottomMargin=1.5 * cm,
            leftMargin=1.2 * cm,
            rightMargin=1.2 * cm,
        )
        story = []
        styles = getSampleStyleSheet()

        department_style = styles['Normal'].clone('DepartmentStyle')
        department_style.alignment = 1
        department_style.fontSize = 14
        department_style.fontName = 'Times-Bold'
        department_style.leading = 16

        exam_style = styles['Normal'].clone('ExamStyle')
        exam_style.alignment = 1
        exam_style.fontSize = 12
        exam_style.fontName = 'Times-Bold'
        exam_style.leading = 14

        subtitle_style = styles['Normal'].clone('SubTitleStyle')
        subtitle_style.alignment = 1
        subtitle_style.fontSize = 11
        subtitle_style.fontName = 'Times-Bold'
        subtitle_style.leading = 13

        info_style = styles['Normal'].clone('InfoStyle')
        info_style.fontName = 'Times-Roman'
        info_style.fontSize = 9
        info_style.leading = 12

        pair_left_style = styles['Normal'].clone('PairLeftStyle')
        pair_left_style.alignment = 0
        pair_left_style.fontName = 'Times-Roman'
        pair_left_style.fontSize = 9
        pair_left_style.leading = 11

        pair_right_style = styles['Normal'].clone('PairRightStyle')
        pair_right_style.alignment = 2
        pair_right_style.fontName = 'Times-Roman'
        pair_right_style.fontSize = 9
        pair_right_style.leading = 11

        def pair_text(label, value, right=False):
            style = pair_right_style if right else pair_left_style
            return Paragraph(f"<b>{label}:</b> {value or '-'}", style)

        def add_header(subtitle='Attendance Sheet'):
            banner = get_banner_image()
            if banner:
                story.append(banner)
            story.append(Spacer(1, 0.08 * cm))
            story.append(Paragraph(meta['department'] or '-', department_style))
            story.append(Spacer(1, 0.05 * cm))
            story.append(Paragraph(meta['exam_name'], exam_style))
            story.append(Paragraph(subtitle, subtitle_style))
            story.append(Spacer(1, 0.08 * cm))

            details = [
                [pair_text('Course Name', meta['course_name']), pair_text('Course Code', meta['course_code'], right=True)],
                [pair_text('Exam Date', meta['exam_date']), pair_text('Room', room_name or 'All Rooms', right=True)],
            ]

            meta_table = Table(details, colWidths=[9.3 * cm, 9.3 * cm], hAlign='LEFT')
            meta_table.setStyle(TableStyle([
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('LEFTPADDING', (0, 0), (0, -1), 0),
                ('RIGHTPADDING', (0, 0), (0, -1), 8),
                ('LEFTPADDING', (1, 0), (1, -1), 8),
                ('RIGHTPADDING', (1, 0), (1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 2.5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
                ('LINEBELOW', (0, -1), (-1, -1), 0.4, colors.HexColor('#AAAAAA')),
            ]))
            story.append(meta_table)
            story.append(Spacer(1, 0.18 * cm))

        max_rows_first = 33
        max_rows_next = 45
        chunks = [students[:max_rows_first]]
        remaining = students[max_rows_first:]
        for i in range(0, len(remaining), max_rows_next):
            chunks.append(remaining[i:i + max_rows_next])

        for idx, chunk in enumerate(chunks):
            if idx > 0:
                story.append(PageBreak())
            subtitle = 'Attendance Sheet' if idx == 0 else 'Attendance Sheet (Continued)'
            add_header(subtitle=subtitle)

            table_data = [['S.No.', 'Enrollment No', 'Student Name', 'Code', 'Password', 'Signature']]
            for row_idx, student in enumerate(chunk, start=(idx * max_rows_next) + 1):
                table_data.append([
                    str(row_idx),
                    str(student.get('enrollment', '')),
                    str(student.get('name', ''))[:28],
                    str(student.get('code', '')),
                    str(student.get('password', '')),
                    '',
                ])

            student_table = Table(
                table_data,
                colWidths=[1.0 * cm, 3.2 * cm, 5.5 * cm, 2.0 * cm, 2.4 * cm, 4.5 * cm],
                repeatRows=1,
            )
            student_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E8E8E8')),
                ('GRID', (0, 0), (-1, -1), 0.6, colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Times-Roman'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ALIGN', (2, 1), (2, -1), 'LEFT'),
                ('LEFTPADDING', (2, 1), (2, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ]))
            story.append(student_table)

        story.append(Spacer(1, 0.24 * cm))

        summary_data = [
            [Paragraph(f"<b>No. of Students Registered = {len(students)}</b>", info_style)],
            [Paragraph('<b>No. of Students Appeared =</b>', info_style)],
            [Paragraph('<b>No. of Students Absent =</b>', info_style)],
            [Paragraph('<b>No. of Students Detained =</b>', info_style)],
        ]
        summary_table = Table(summary_data, colWidths=[18.6 * cm])
        summary_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.6, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.36 * cm))

        sig_data = [[
            Paragraph(
                f"<b>1. Signature & Name of Invigilator</b><br/><br/>"
                f"<u>_________________</u><br/>{meta['invigilator_1'] or ''}",
                info_style,
            ),
            Paragraph(
                f"<b>2. Signature & Name of Invigilator</b><br/><br/>"
                f"<u>_________________</u><br/>{meta['invigilator_2'] or ''}",
                info_style,
            ),
        ]]
        sig_table = Table(sig_data, colWidths=[9.2 * cm, 9.4 * cm])
        sig_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        story.append(sig_table)

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception as e:
        logger.error('Error generating attendance PDF: %s', e, exc_info=True)
        return None


def generate_master_plan_pdf(plan_data: dict, template_data: dict = None, user_id: str = None) -> bytes:
    """Generate master seating plan PDF with improved heading/details spacing."""
    try:
        if template_data is None and user_id:
            template_data = template_manager.get_user_template(user_id)
        if template_data is None:
            template_data = {}

        meta = _master_metadata(plan_data, template_data)
        rooms = _normalize_rooms(plan_data)

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            topMargin=1.2 * cm,
            bottomMargin=1.5 * cm,
            leftMargin=1.2 * cm,
            rightMargin=1.2 * cm,
        )
        story = []
        styles = getSampleStyleSheet()

        department_style = styles['Normal'].clone('MasterDepartmentStyle')
        department_style.alignment = 1
        department_style.fontName = 'Times-Bold'
        department_style.fontSize = 14
        department_style.leading = 16

        heading_style = styles['Normal'].clone('HeadingStyle')
        heading_style.alignment = 1
        heading_style.fontName = 'Times-Bold'
        heading_style.fontSize = 12
        heading_style.leading = 14

        subheading_style = styles['Normal'].clone('SubHeadingStyle')
        subheading_style.alignment = 1
        subheading_style.fontName = 'Times-Bold'
        subheading_style.fontSize = 13
        subheading_style.leading = 14

        pair_left_style = styles['Normal'].clone('MasterPairLeftStyle')
        pair_left_style.alignment = 0
        pair_left_style.fontName = 'Times-Roman'
        pair_left_style.fontSize = 9
        pair_left_style.leading = 11

        pair_right_style = styles['Normal'].clone('MasterPairRightStyle')
        pair_right_style.alignment = 2
        pair_right_style.fontName = 'Times-Roman'
        pair_right_style.fontSize = 9
        pair_right_style.leading = 11

        def pair_text(label, value, right=False):
            style = pair_right_style if right else pair_left_style
            return Paragraph(f"<b>{label}:</b> {value or '-'}", style)

        banner = get_banner_image()
        if banner:
            story.append(banner)
        story.append(Spacer(1, 0.08 * cm))
        story.append(Paragraph(meta['department'] or '-', department_style))

        # Corrected heading/detail spacing (task #8)
        story.append(Spacer(1, 0.10 * cm))
        story.append(Paragraph(meta['exam_name'], heading_style))
        story.append(Spacer(1, 0.06 * cm))
        story.append(Paragraph('Master Seating Plan', subheading_style))
        story.append(Spacer(1, 0.14 * cm))

        details = [
            [pair_text('Course Name', meta['course_name']), pair_text('Course Code', meta['course_code'], right=True)],
            [pair_text('Exam Date', meta['exam_date']), pair_text('Total Rooms', str(len(rooms)), right=True)],
        ]
        details_table = Table(details, colWidths=[9.3 * cm, 9.3 * cm], hAlign='LEFT')
        details_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('LEFTPADDING', (0, 0), (0, -1), 0),
            ('RIGHTPADDING', (0, 0), (0, -1), 8),
            ('LEFTPADDING', (1, 0), (1, -1), 8),
            ('RIGHTPADDING', (1, 0), (1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 2.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
            ('LINEBELOW', (0, -1), (-1, -1), 0.4, colors.HexColor('#AAAAAA')),
        ]))
        story.append(details_table)
        story.append(Spacer(1, 0.20 * cm))

        table_data = [[
            'S.No', 'Branch', 'Semester', 'Room No.', 'From', 'To', 'Total', 'Grand Total'
        ]]

        serial = 1
        grand_total = 0
        for room in rooms:
            room_name = room.get('room_name', '')
            branch_allocs = room.get('branch_allocations', {})
            room_total = room.get('total_students', 0)
            grand_total += room_total

            first_row = True
            for branch_name, alloc in branch_allocs.items():
                table_data.append([
                    str(serial) if first_row else '',
                    branch_name,
                    '-',
                    room_name if first_row else '',
                    alloc.get('from_roll', ''),
                    alloc.get('to_roll', ''),
                    str(alloc.get('count', 0)),
                    str(room_total) if first_row else '',
                ])
                first_row = False
            serial += 1

        if len(table_data) == 1:
            table_data.append(['', '-', '-', '-', '-', '-', '0', '0'])

        table_data.append(['', '', '', '', 'Total', '', str(grand_total), ''])

        table = Table(
            table_data,
            colWidths=[1.1 * cm, 2.7 * cm, 1.5 * cm, 2.2 * cm, 3.0 * cm, 3.0 * cm, 1.2 * cm, 1.6 * cm],
            repeatRows=1,
        )
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E8E8E8')),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#FFF5CC')),
            ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
            ('FONTNAME', (0, 1), (-1, -2), 'Times-Roman'),
            ('FONTNAME', (0, -1), (-1, -1), 'Times-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.6, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(table)
        story.append(Spacer(1, 0.26 * cm))

        admin_rows = [
            [pair_text('Chief Invigilator', meta['invigilator_1']), pair_text('Invigilator 2', meta['invigilator_2'], right=True)],
            [pair_text('Invigilator 3', meta['invigilator_3']), Paragraph('', pair_right_style)],
        ]
        admin_table = Table(admin_rows, colWidths=[9.3 * cm, 9.3 * cm], hAlign='LEFT')
        admin_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('LEFTPADDING', (0, 0), (0, -1), 0),
            ('RIGHTPADDING', (0, 0), (0, -1), 8),
            ('LEFTPADDING', (1, 0), (1, -1), 8),
            ('RIGHTPADDING', (1, 0), (1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 2.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
            ('LINEBELOW', (0, -1), (-1, -1), 0.4, colors.HexColor('#AAAAAA')),
        ]))
        story.append(admin_table)
        story.append(Spacer(1, 0.45 * cm))

        sign_style = styles['Normal'].clone('SignStyle')
        sign_style.fontName = 'Times-Roman'
        sign_style.fontSize = 9

        left_sign_name = template_data.get('major_coordinator_name', 'Exam Coordinator')
        left_sign_title = template_data.get('major_coordinator_title', 'Dept. Exam Coordinator')
        right_sign_name = template_data.get('major_hod_name', 'Head of Department')
        right_sign_title = template_data.get('major_hod_title', 'HOD')

        sig_table = Table([[
            Paragraph(f"<b>{left_sign_title}</b><br/><br/><u>_________________</u><br/>{left_sign_name}", sign_style),
            Paragraph('', sign_style),
            Paragraph(f"<b>{right_sign_title}</b><br/><br/><u>_________________</u><br/>{right_sign_name}", sign_style),
        ]], colWidths=[5.2 * cm, 2.8 * cm, 5.2 * cm])
        sig_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('ALIGN', (2, 0), (2, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(sig_table)

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception as e:
        logger.error('Error generating master plan PDF: %s', e, exc_info=True)
        return None


@major_exam_attendance_bp.route('/download/pdf/<plan_id>', methods=['GET'])
@token_required
def download_attendance_pdf(plan_id):
    """Download attendance PDF, optionally filtered by room and branch."""
    try:
        user_id = request.user_id
        room_name = request.args.get('room')
        branch_filter = request.args.get('branch')

        plan = cache_manager.retrieve_plan(user_id, plan_id)
        if not plan:
            return jsonify({'error': 'Plan not found'}), 404

        template = template_manager.get_user_template(user_id)
        pdf_data = generate_attendance_pdf(
            plan,
            room_name=room_name,
            branch_filter=branch_filter,
            template_data=template,
            user_id=user_id,
        )
        if not pdf_data:
            return jsonify({'error': 'PDF generation failed'}), 500

        filename_parts = ['MAJOR_EXAM_ATTENDANCE', plan_id]
        if room_name:
            filename_parts.append(room_name.replace(' ', '_'))
        if branch_filter:
            filename_parts.append(branch_filter)
        filename = '_'.join(filename_parts) + '.pdf'

        return send_file(
            io.BytesIO(pdf_data),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename,
        )
    except Exception as e:
        logger.error('Error downloading attendance PDF: %s', e, exc_info=True)
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@major_exam_attendance_bp.route('/download/master-plan/<plan_id>', methods=['GET'])
@token_required
def download_master_plan(plan_id):
    """Download master seating plan PDF."""
    try:
        user_id = request.user_id
        plan = cache_manager.retrieve_plan(user_id, plan_id)
        if not plan:
            return jsonify({'error': 'Plan not found'}), 404

        template = template_manager.get_user_template(user_id)
        pdf_data = generate_master_plan_pdf(plan, template_data=template, user_id=user_id)
        if not pdf_data:
            return jsonify({'error': 'PDF generation failed'}), 500

        return send_file(
            io.BytesIO(pdf_data),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'MAJOR_EXAM_MASTER_PLAN_{plan_id}.pdf',
        )
    except Exception as e:
        logger.error('Error downloading master plan PDF: %s', e, exc_info=True)
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@major_exam_attendance_bp.route('/rooms/<plan_id>', methods=['GET'])
@token_required
def get_plan_rooms(plan_id):
    """Return room breakdown + stored metadata for plan viewer."""
    try:
        user_id = request.user_id
        plan = cache_manager.retrieve_plan(user_id, plan_id)
        if not plan:
            return jsonify({'error': 'Plan not found'}), 404

        rooms = _normalize_rooms(plan)
        room_data = []
        for room in rooms:
            branches_info = {}
            for branch, alloc in room.get('branch_allocations', {}).items():
                branches_info[branch] = {
                    'count': alloc.get('count', 0),
                    'from_roll': alloc.get('from_roll', ''),
                    'to_roll': alloc.get('to_roll', ''),
                }
            room_data.append({
                'room_name': room.get('room_name', ''),
                'capacity': room.get('capacity', 0),
                'total_students': room.get('total_students', 0),
                'branches': branches_info,
            })

        return jsonify({
            'success': True,
            'plan_id': plan_id,
            'status': plan.get('metadata', {}).get('status', ''),
            'rooms': room_data,
            'attendance_metadata': plan.get('attendance_metadata', {}),
            'master_metadata': plan.get('master_metadata', {}),
        }), 200
    except Exception as e:
        logger.error('Error fetching plan rooms: %s', e, exc_info=True)
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@major_exam_attendance_bp.route('/plan-info/<plan_id>', methods=['GET'])
@token_required
def plan_info(plan_id):
    """Return lightweight plan info for major tools pages."""
    try:
        user_id = request.user_id
        plan = cache_manager.retrieve_plan(user_id, plan_id)
        if not plan:
            return jsonify({'error': 'Plan not found'}), 404

        metadata = plan.get('metadata', {})
        normalized_rooms = _normalize_rooms(plan)
        plan_info_data = {
            'plan_id': plan.get('plan_id'),
            'created_at': plan.get('created_at'),
            'status': metadata.get('status', 'unknown'),
            'total_students': metadata.get('total_students', len(_flatten_students_from_plan(plan))),
            'allocated_count': metadata.get('allocated_count', 0),
            'room_count': metadata.get('room_count', len(normalized_rooms)),
        }
        return jsonify({'success': True, 'plan_info': plan_info_data}), 200
    except Exception as e:
        logger.error('Error fetching plan info: %s', e, exc_info=True)
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@major_exam_attendance_bp.route('/metadata/<plan_id>', methods=['POST'])
@token_required
def save_attendance_metadata(plan_id):
    """Save global attendance metadata."""
    try:
        user_id = request.user_id
        data = request.json or {}

        plan = cache_manager.retrieve_plan(user_id, plan_id)
        if not plan:
            return jsonify({'error': 'Plan not found'}), 404

        if 'attendance_metadata' not in plan:
            plan['attendance_metadata'] = {}

        plan['attendance_metadata']['exam_name'] = data.get('exam_name', '')
        plan['attendance_metadata']['department'] = data.get('department', '')
        plan['attendance_metadata']['course_name'] = data.get('course_name', '')
        plan['attendance_metadata']['course_code'] = data.get('course_code', '')
        plan['attendance_metadata']['exam_date'] = data.get('examDate', '')
        plan['attendance_metadata']['notes'] = data.get('notes', '')
        plan['attendance_metadata']['invigilator_1'] = data.get('invigilator1', '')
        plan['attendance_metadata']['invigilator_2'] = data.get('invigilator2', '')
        plan['attendance_metadata']['invigilator_3'] = data.get('invigilator3', '')

        success = cache_manager.store_plan(user_id, plan_id, plan)
        if not success:
            return jsonify({'error': 'Failed to store metadata'}), 500

        return jsonify({'success': True, 'message': 'Attendance metadata saved'}), 200
    except Exception as e:
        logger.error('Error saving attendance metadata: %s', e, exc_info=True)
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@major_exam_attendance_bp.route('/master-metadata/<plan_id>', methods=['POST'])
@token_required
def save_master_metadata(plan_id):
    """Save master-plan-specific metadata (required subset)."""
    try:
        user_id = request.user_id
        data = request.json or {}

        plan = cache_manager.retrieve_plan(user_id, plan_id)
        if not plan:
            return jsonify({'error': 'Plan not found'}), 404

        if 'master_metadata' not in plan:
            plan['master_metadata'] = {}

        plan['master_metadata']['exam_name'] = data.get('exam_name', '')
        plan['master_metadata']['department'] = data.get('department', '')
        plan['master_metadata']['course_name'] = data.get('course_name', '')
        plan['master_metadata']['course_code'] = data.get('course_code', '')
        plan['master_metadata']['exam_date'] = data.get('examDate', '')
        plan['master_metadata']['invigilator_1'] = data.get('invigilator1', '')
        plan['master_metadata']['invigilator_2'] = data.get('invigilator2', '')
        plan['master_metadata']['invigilator_3'] = data.get('invigilator3', '')

        success = cache_manager.store_plan(user_id, plan_id, plan)
        if not success:
            return jsonify({'error': 'Failed to store metadata'}), 500

        return jsonify({'success': True, 'message': 'Master metadata saved'}), 200
    except Exception as e:
        logger.error('Error saving master metadata: %s', e, exc_info=True)
        return jsonify({'error': f'Server error: {str(e)}'}), 500
