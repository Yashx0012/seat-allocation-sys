"""
Major Exam Attendance Blueprint
Handles professional PDF generation for attendance sheets
Matches quality standards of minor exam implementations
"""
from flask import Blueprint, request, jsonify, send_file
import io
import os
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from datetime import datetime

from algo.services.auth_service import token_required
from algo.core.cache.major_exam_cache import get_major_cache_manager
from algo.core.cache.major_exam_template_manager import MajorExamTemplateManager

major_exam_attendance_bp = Blueprint('major_exam_attendance', __name__, url_prefix='/api/major-exam')
cache_manager = get_major_cache_manager()
template_manager = MajorExamTemplateManager()

# Banner image path
_BASE_DIR = Path(__file__).resolve().parent.parent.parent
BANNER_PATH = str(_BASE_DIR / "pdf_gen" / "data" / "banner.png")


def get_banner_image():
    """Load banner image if available, return None otherwise"""
    if os.path.exists(BANNER_PATH):
        try:
            return Image(BANNER_PATH, width=18.6*cm, height=3*cm, kind='proportional')
        except Exception:
            return None
    return None


def generate_attendance_pdf(plan_data: dict, template_data: dict = None, user_id: str = None) -> bytes:
    """
    Generate professional attendance sheet PDF with:
    - Banner header with department info (from template if available)
    - Metadata display (course, date, time)
    - Color-coded styling with proper typography
    - Professional table layout with pagination
    - Summary statistics
    - Invigilator signature section
    
    Args:
        plan_data: Plan data dict with students, metadata
        template_data: Optional template data with custom headers
        user_id: Optional user_id to fetch template if template_data not provided
    """
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4,
            topMargin=1.2*cm, 
            bottomMargin=1.5*cm,
            leftMargin=1.2*cm, 
            rightMargin=1.2*cm
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        # Fetch template if not provided
        if template_data is None and user_id:
            template_data = template_manager.get_user_template(user_id)
        if template_data is None:
            template_data = {}
        
        # ===== CUSTOM STYLES =====
        header_style = styles['Normal'].clone('HeaderStyle')
        header_style.alignment = 1  # Center
        header_style.fontSize = 11
        header_style.fontName = 'Times-Roman'
        
        title_style = styles['Normal'].clone('TitleStyle')
        title_style.alignment = 1
        title_style.fontSize = 13
        title_style.textColor = colors.HexColor('#FF8C00')  # Orange for major exam
        title_style.fontName = 'Times-Bold'
        title_style.spaceAfter = 8
        
        info_style = styles['Normal'].clone('InfoStyle')
        info_style.fontSize = 9
        info_style.fontName = 'Times-Roman'
        
        # ===== BANNER SECTION =====
        banner = get_banner_image()
        if banner:
            story.append(banner)
        else:
            # Use template department name or fallback
            dept_name = template_data.get('major_exam_dept_name', 'Department of Computer Science & Engineering')
            story.append(Paragraph(f"<u><b>{dept_name}</b></u>", header_style))
        
        story.append(Spacer(1, 0.15*cm))
        
        # ===== TITLE SECTION =====
        plan_id = plan_data.get('plan_id', 'MAJOR-EXAM-PLAN')
        # Use template exam heading or from plan data
        exam_name = template_data.get('major_exam_heading', plan_data.get('exam_name', 'MAJOR EXAMINATION'))
        story.append(Paragraph(f"<b>{exam_name}</b>", title_style))
        story.append(Spacer(1, 0.1*cm))
        
        # ===== METADATA INFO TABLE =====
        course_name = plan_data.get('course_name', 'N/A')
        course_code = plan_data.get('course_code', 'N/A')
        exam_date = plan_data.get('date', datetime.now().strftime('%d.%m.%Y'))
        exam_time = plan_data.get('time', 'N/A')
        
        meta_data = [
            [Paragraph(f"<b>Course Name:</b> {course_name}", info_style), 
             Paragraph(f"<b>Course Code:</b> {course_code}", info_style)],
            [Paragraph(f"<b>Date:</b> {exam_date}", info_style), 
             Paragraph(f"<b>Time:</b> {exam_time}", info_style)]
        ]
        meta_table = Table(meta_data, colWidths=[9.5*cm, 8.5*cm])
        meta_table.setStyle(TableStyle([
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
            ('FONTSIZE', (0, 0), (-1, -1), 9)
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 0.2*cm))
        
        # ===== STUDENT ATTENDANCE TABLE =====
        students = plan_data.get('students', [])
        
        if students:
            # Paginate students (33 per first page, 45 per continuation)
            chunks = []
            if len(students) > 33:
                chunks.append(students[:33])
                remaining = students[33:]
                for i in range(0, len(remaining), 45):
                    chunks.append(remaining[i:i+45])
            else:
                chunks.append(students)
            
            # Process each page chunk
            for chunk_idx, chunk in enumerate(chunks):
                # Build table data
                table_headers = ['S.No.', 'Name', 'Enrollment', 'Code', 'Password', 'Signature']
                table_data = [table_headers]
                
                for idx, student in enumerate(chunk):
                    table_data.append([
                        str(idx + 1),
                        student.get('name', '')[:20],  # Truncate long names
                        student.get('enrollment', ''),
                        student.get('code', ''),
                        student.get('password', ''),
                        ''  # Signature space
                    ])
                
                # Create and style table
                student_table = Table(
                    table_data, 
                    colWidths=[1.0*cm, 4.0*cm, 3.0*cm, 2.2*cm, 2.5*cm, 2.5*cm],
                    repeatRows=0
                )
                student_table.setStyle(TableStyle([
                    # Header styling
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E8E8E8')),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                    ('TOPPADDING', (0, 0), (-1, 0), 4),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    
                    # Content styling
                    ('GRID', (0, 0), (-1, -1), 0.8, colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
                    ('TOPPADDING', (0, 1), (-1, -1), 3),
                    
                    # Left align names
                    ('ALIGN', (1, 1), (1, -1), 'LEFT'),
                ]))
                
                story.append(student_table)
                
                # Add page break between chunks (except last)
                if chunk_idx < len(chunks) - 1:
                    story.append(PageBreak())
        
        story.append(Spacer(1, 0.2*cm))
        
        # ===== SUMMARY STATISTICS SECTION =====
        total_students = len(students) if students else 0
        
        summary_data = [
            [Paragraph(f"<b>No. of Students Registered = {total_students}</b>", info_style)],
            [Paragraph("<b>No. of Students Appeared =</b>", info_style)],
            [Paragraph("<b>No. of Students Absent =</b>", info_style)],
            [Paragraph("<b>No. of Students Detained =</b>", info_style)]
        ]
        
        summary_table = Table(summary_data, colWidths=[18.6*cm])
        summary_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.8, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
            ('FONTSIZE', (0, 0), (-1, -1), 9)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 0.5*cm))
        
        # ===== INVIGILATOR SIGNATURE SECTION =====
        sig_info_style = info_style.clone('SigInfoStyle')
        sig_info_style.fontSize = 8
        
        # Use template coordinator names or defaults
        coordinator_name = template_data.get('major_coordinator_name', 'Exam Coordinator')
        coordinator_title = template_data.get('major_coordinator_title', 'Dept. Exam Coordinator')
        
        sig_data = [[
            Paragraph(f"<b>1. Signature & Name of Invigilator</b><br/><br/><u>_________________</u><br/>{coordinator_name}<br/>{coordinator_title}", sig_info_style),
            Paragraph(f"<b>2. Signature & Name of Invigilator</b><br/><br/><u>_________________</u>", sig_info_style)
        ]]
        
        sig_table = Table(sig_data, colWidths=[9.2*cm, 9.4*cm])
        sig_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(sig_table)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    except Exception as e:
        print(f"❌ Error generating attendance PDF: {e}")
        import traceback
        traceback.print_exc()
        return None


def generate_master_plan_pdf(plan_data: dict, template_data: dict = None, user_id: str = None) -> bytes:
    """
    Generate master seating plan PDF from cached JSON room allocations
    Reads rooms structure with From/To roll number ranges per room/batch
    
    Args:
        plan_data: Plan data dict with rooms structure
        template_data: Optional template data for headers
        user_id: Optional user_id to fetch template if template_data not provided
    """
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4,
            topMargin=1.2*cm, 
            bottomMargin=1.5*cm,
            leftMargin=1.2*cm, 
            rightMargin=1.2*cm
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        # Fetch template if not provided
        if template_data is None and user_id:
            template_data = template_manager.get_user_template(user_id)
        if template_data is None:
            template_data = {}
        
        # ===== CUSTOM STYLES =====
        center_bold = styles['Normal'].clone('CenterBold')
        center_bold.alignment = 1  # Center
        center_bold.fontSize = 11
        center_bold.fontName = 'Times-Bold'
        
        title_style = styles['Normal'].clone('TitleStyle')
        title_style.alignment = 1
        title_style.fontSize = 13
        title_style.fontName = 'Times-Bold'
        
        table_header_style = styles['Normal'].clone('TableHeader')
        table_header_style.alignment = 1
        table_header_style.fontSize = 9
        table_header_style.fontName = 'Times-Bold'
        
        table_cell_style = styles['Normal'].clone('TableCell')
        table_cell_style.alignment = 1
        table_cell_style.fontSize = 8
        table_cell_style.fontName = 'Times-Roman'
        
        # ===== BANNER SECTION =====
        banner = get_banner_image()
        if banner:
            story.append(banner)
        else:
            # Use template department name
            dept_name = template_data.get('major_exam_dept_name', 'Department of Computer Science & Engineering')
            story.append(Paragraph(dept_name, center_bold))
        
        story.append(Spacer(1, 0.1*cm))
        
        # ===== TITLE SECTION =====
        # Use template exam heading
        exam_name = template_data.get('major_exam_heading', 'EXAMINATION')
        story.append(Paragraph(exam_name, title_style))
        story.append(Paragraph("Master Seating Plan", title_style))
        
        exam_date = plan_data.get('metadata', {}).get('date', datetime.now().strftime('%d.%m.%Y'))
        story.append(Paragraph(f"Date: {exam_date}", table_header_style))
        story.append(Spacer(1, 0.2*cm))
        
        # ===== BUILD ROOM-WISE ALLOCATION TABLE =====
        # Extract rooms structure from cached plan (populated by allocate endpoint)
        rooms = plan_data.get('rooms', {})
        
        if not rooms:
            story.append(Paragraph("No room allocations available", table_header_style))
            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()
        
        # Build table data with headers
        table_data = [
            [
                Paragraph('<b>S.No</b>', table_header_style),
                Paragraph('<b>Branch</b>', table_header_style),
                Paragraph('<b>Semester</b>', table_header_style),
                Paragraph('<b>Room No.</b>', table_header_style),
                Paragraph('<b>From</b>', table_header_style),
                Paragraph('<b>To</b>', table_header_style),
                Paragraph('<b>Total</b>', table_header_style),
                Paragraph('<b>Grand Total</b>', table_header_style),
            ]
        ]
        
        # Extract allocations from rooms
        serial_no = 1
        branch_totals = {}
        
        for room_name, room_data in rooms.items():
            batches = room_data.get('batches', {})
            
            for batch_label, batch_info in batches.items():
                branch = batch_info.get('info', {}).get('branch', 'CSE')
                semester = batch_info.get('info', {}).get('semester', 'IV')
                from_roll = batch_info.get('from_roll', 'N/A')
                to_roll = batch_info.get('to_roll', 'N/A')
                total = batch_info.get('total', 0)
                
                # Track grand totals per branch
                if branch not in branch_totals:
                    branch_totals[branch] = 0
                branch_totals[branch] += total
                
                table_data.append([
                    Paragraph(str(serial_no), table_cell_style),
                    Paragraph(branch, table_cell_style),
                    Paragraph(semester, table_cell_style),
                    Paragraph(room_name, table_cell_style),
                    Paragraph(from_roll, table_cell_style),
                    Paragraph(to_roll, table_cell_style),
                    Paragraph(str(total), table_cell_style),
                    Paragraph('', table_cell_style),  # Grand total will be filled per branch
                ])
                
                serial_no += 1
        
        # Total row
        total_count = sum(branch_totals.values())
        table_data.append([
            Paragraph('', table_header_style),
            Paragraph('', table_header_style),
            Paragraph('', table_header_style),
            Paragraph('', table_header_style),
            Paragraph('<b>Total</b>', table_header_style),
            Paragraph('', table_header_style),
            Paragraph(f'<b>{total_count}</b>', table_header_style),
            Paragraph('', table_header_style),
        ])
        
        # Create table
        allocation_table = Table(table_data, colWidths=[1.2*cm, 2.2*cm, 1.5*cm, 1.8*cm, 2.5*cm, 2.5*cm, 1.2*cm, 1.5*cm])
        allocation_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E8E8E8')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('PADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#FFFFCC')),
            ('FONTNAME', (0, -1), (-1, -1), 'Times-Bold'),
        ]))
        
        story.append(allocation_table)
        story.append(Spacer(1, 0.5*cm))
        
        # ===== INVIGILATOR & METADATA SECTION =====
        # Get metadata from plan
        attendance_meta = plan_data.get('attendance_metadata', {})
        exam_date_meta = attendance_meta.get('exam_date', plan_data.get('metadata', {}).get('date', ''))
        invig_1 = attendance_meta.get('invigilator_1', '')
        invig_2 = attendance_meta.get('invigilator_2', '')
        invig_3 = attendance_meta.get('invigilator_3', '')
        
        # Add metadata section
        meta_style = styles['Normal'].clone('MetaStyle')
        meta_style.fontSize = 10
        meta_style.fontName = 'Times-Bold'
        
        if exam_date_meta or invig_1 or invig_2 or invig_3:
            story.append(Paragraph("<b>EXAM ADMINISTRATION DETAILS</b>", meta_style))
            
            # Create metadata table
            meta_data = [
                ['Exam Date:', exam_date_meta or 'Not Specified'],
                ['Chief Invigilator:', invig_1 or 'Not Assigned'],
                ['Invigilator 2:', invig_2 or 'Not Assigned'],
                ['Invigilator 3:', invig_3 or 'Not Assigned'],
            ]
            
            meta_table = Table(meta_data, colWidths=[5*cm, 8*cm])
            meta_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Times-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('PADDING', (0, 0), (-1, -1), 5),
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F0F0F0')),
            ]))
            
            story.append(meta_table)
            story.append(Spacer(1, 0.5*cm))
        
        # ===== SIGNATURE SECTION =====
        sig_style = styles['Normal'].clone('SigStyle')
        sig_style.fontSize = 9
        sig_style.fontName = 'Times-Roman'
        
        # Use template coordinator names
        coordinator_name = template_data.get('major_coordinator_name', 'Exam Coordinator')
        coordinator_title = template_data.get('major_coordinator_title', 'Dept. Exam Coordinator')
        hod_name = template_data.get('major_hod_name', 'Head of Department')
        hod_title = template_data.get('major_hod_title', 'HOD')
        
        sig_data = [[
            Paragraph(f'<b>{coordinator_title}</b><br/><br/><u>_________________</u><br/>{coordinator_name}', sig_style),
            Paragraph('', sig_style),
            Paragraph(f'<b>{hod_title}</b><br/><br/><u>_________________</u><br/>{hod_name}', sig_style),
        ]]
        
        sig_table = Table(sig_data, colWidths=[5*cm, 3*cm, 5*cm])
        sig_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'CENTER'),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(sig_table)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    except Exception as e:
        print(f"❌ Error generating master plan PDF: {e}")
        import traceback
        traceback.print_exc()
        return None

@major_exam_attendance_bp.route('/download/pdf/<plan_id>', methods=['GET'])
@token_required
def download_attendance_pdf(plan_id):
    """
    Download professional attendance sheet PDF with dynamic template headers
    Endpoint: GET /api/major-exam/download/pdf/<plan_id>
    """
    try:
        user_id = request.user_id
        
        # Retrieve plan from cache
        plan = cache_manager.retrieve_plan(user_id, plan_id)
        if not plan:
            return jsonify({'error': 'Plan not found', 'plan_id': plan_id}), 404
        
        # Fetch user template for dynamic headers
        template = template_manager.get_user_template(user_id)
        
        # Generate PDF with professional formatting and template integration
        pdf_data = generate_attendance_pdf(plan, template_data=template, user_id=user_id)
        if not pdf_data:
            return jsonify({'error': 'PDF generation failed'}), 500
        
        # Return PDF as downloadable file
        return send_file(
            io.BytesIO(pdf_data),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'MAJOR_EXAM_ATTENDANCE_{plan_id}.pdf'
        )
    
    except Exception as e:
        print(f"❌ Error downloading attendance PDF: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@major_exam_attendance_bp.route('/download/master-plan/<plan_id>', methods=['GET'])
@token_required
def download_master_plan(plan_id):
    """
    Download master seating plan PDF analyzing the cached JSON allocation data
    For major exams: generates institutional master plan with room-wise summary
    Uses template data for dynamic headers
    Endpoint: GET /api/major-exam/download/master-plan/<plan_id>
    """
    try:
        user_id = request.user_id
        
        # Retrieve plan from major exam cache (analyzes JSON)
        plan = cache_manager.retrieve_plan(user_id, plan_id)
        if not plan:
            return jsonify({'error': 'Plan not found', 'plan_id': plan_id}), 404
        
        # Fetch user template for dynamic headers
        template = template_manager.get_user_template(user_id)
        
        # Check if plan has room allocations (structured data)
        # If it does, use the institutional master plan format
        if 'rooms' in plan and plan.get('metadata', {}).get('status') == 'FINALIZED':
            # Use the master plan PDF generator for finalized multi-room plans
            from algo.api.blueprints.master_plan_pdf import _build_master_plan_pdf
            
            pdf_buffer = _build_master_plan_pdf(
                snapshot=plan,
                user_id=user_id,
                dept_name=template.get('major_exam_dept_name', 'Department of Computer Science & Engineering'),
                exam_name=template.get('major_exam_heading', 'MAJOR EXAMINATION'),
                date_text=plan.get('metadata', {}).get('date', ''),
                title='Master Seating Plan',
                left_sign_name=template.get('major_coordinator_name', ''),
                left_sign_title=template.get('major_coordinator_title', 'Exam Coordinator'),
                right_sign_name=template.get('major_hod_name', ''),
                right_sign_title=template.get('major_hod_title', 'HOD'),
            )
            
            return send_file(
                pdf_buffer,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'MAJOR_EXAM_MASTER_PLAN_{plan_id}.pdf'
            )
        else:
            # For non-finalized or simple plans, generate master plan from metadata summary
            pdf_data = generate_master_plan_pdf(plan, template_data=template, user_id=user_id)
            if not pdf_data:
                return jsonify({'error': 'PDF generation failed'}), 500
            
            return send_file(
                io.BytesIO(pdf_data),
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'MAJOR_EXAM_MASTER_PLAN_{plan_id}.pdf'
            )
    
    except Exception as e:
        print(f"❌ Error generating master plan PDF: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@major_exam_attendance_bp.route('/metadata/<plan_id>', methods=['POST'])
@token_required
def save_attendance_metadata(plan_id):
    """
    Save attendance metadata (invigilators, exam date) to plan
    Endpoint: POST /api/major-exam/metadata/<plan_id>
    Body: {examDate, invigilator1, invigilator2, invigilator3}
    """
    try:
        user_id = request.user_id
        data = request.json or {}
        
        print(f"\n💾 SAVE ATTENDANCE METADATA")
        print(f"   User ID: {user_id}")
        print(f"   Plan ID: {plan_id}")
        print(f"   Data: {data}")
        
        # Retrieve plan
        plan = cache_manager.retrieve_plan(user_id, plan_id)
        if not plan:
            print(f"   ERROR: Plan not found")
            return jsonify({'error': 'Plan not found'}), 404
        
        # Save metadata (C4: All 9 fields)
        if 'attendance_metadata' not in plan:
            plan['attendance_metadata'] = {}
        
        plan['attendance_metadata']['exam_date'] = data.get('examDate', '')
        plan['attendance_metadata']['exam_name'] = data.get('exam_name', '')
        plan['attendance_metadata']['department'] = data.get('department', '')
        plan['attendance_metadata']['course_name'] = data.get('course_name', '')
        plan['attendance_metadata']['course_code'] = data.get('course_code', '')
        plan['attendance_metadata']['notes'] = data.get('notes', '')
        plan['attendance_metadata']['invigilator_1'] = data.get('invigilator1', '')
        plan['attendance_metadata']['invigilator_2'] = data.get('invigilator2', '')
        plan['attendance_metadata']['invigilator_3'] = data.get('invigilator3', '')
        
        # Store back
        success = cache_manager.store_plan(user_id, plan_id, plan)
        
        if not success:
            print(f"   ERROR: Failed to store metadata")
            return jsonify({'error': 'Failed to store metadata'}), 500
        
        print(f"   ✅ Metadata saved successfully")
        return jsonify({'success': True, 'message': 'Metadata saved'}), 200
    
    except Exception as e:
        logger.error(f"Error saving attendance metadata: {e}", exc_info=True)
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500
