import os
import io
import pandas as pd
import re
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm

def get_banner():
    banner_path = os.path.join(os.path.dirname(__file__), 'banner.png')
    if os.path.exists(banner_path):
        return Image(banner_path, width=18.6*cm, height=3*cm, kind='proportional')
    return None

def generate_attendance_pdf(allocation, metadata):
    """Generate attendance PDF using ReportLab with exact Seat Allocation format in-memory"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=15, bottomMargin=20,
        leftMargin=1.2*cm, rightMargin=1.2*cm
    )
    story = []
    styles = getSampleStyleSheet()
    header_style = styles['Heading2']
    header_style.alignment = 1

    dept_name = metadata.get('dept_name', 'Department of Computer Science & Engineering')
    exam = metadata.get('exam_name', 'IV Sem Quiz')
    date_text = metadata.get('date_text', '08.04.2026')

    for room_data in allocation:
        room_name = room_data['room']
        students = room_data['students']
        if students.empty:
            continue
        
        chunks = []
        if len(students) > 33:
            chunks.append(students.iloc[:33])
            remaining = students.iloc[33:]
            for i in range(0, len(remaining), 45):
                chunks.append(remaining.iloc[i:i+45])
        else:
            chunks.append(students)

        for chunk_idx, chunk in enumerate(chunks):
            if chunk_idx == 0:
                banner = get_banner()
                if banner:
                    story.append(banner)
                else:
                    story.append(Paragraph(f"<u><b>{dept_name}</b></u>", header_style))
                    
                story.append(Spacer(1, 0.2*cm))
                story.append(Paragraph(f"<b>Attendance Sheet - {exam}</b>", header_style))
                story.append(Spacer(1, 0.2*cm))
                story.append(Paragraph(f"<b>Date: {date_text}</b>", styles['Normal']))
                story.append(Paragraph(f"<b>Room No: {room_name}</b>", styles['Normal']))
                story.append(Spacer(1, 0.5*cm))
            else:
                # Add minimal header for continued pages
                story.append(Paragraph(f"<b>Attendance Sheet - {exam} (Continued)</b>", header_style))
                story.append(Spacer(1, 0.2*cm))
                story.append(Paragraph(f"<b>Room No: {room_name}</b>", styles['Normal']))
                story.append(Spacer(1, 0.5*cm))
            
            table_data = [['S.No.', 'Enrollment No', 'Student Name', 'Code', 'Password', 'Signature']]
            
            # Dynamically identify exact column names to handle any Excel typos
            enroll_col = next((c for c in chunk.columns if 'ENROLL' in str(c)), 'ENROLLMENT')
            name_col = next((c for c in chunk.columns if 'NAME' in str(c)), 'STUDENT NAME')
            code_col = next((c for c in chunk.columns if 'CODE' in str(c)), 'CODE')
            pass_col = next((c for c in chunk.columns if 'PASS' in str(c)), 'PASSWORD')
            
            for idx, row in chunk.iterrows():
                # Get actual row number
                s_no = str(idx + 1)
                enrollment = str(row.get(enroll_col, '')).strip()
                name = str(row.get(name_col, '')).strip()
                code = str(row.get(code_col, '')).strip()
                password = str(row.get(pass_col, '')).strip()
                
                # Handle pandas NaN stringification
                if enrollment.lower() == 'nan': enrollment = ''
                if name.lower() == 'nan': name = ''
                if code.lower() == 'nan': code = ''
                if password.lower() == 'nan': password = ''
                
                # Handle floats and weird excel types correctly
                if password.endswith('.0'):
                    password = password[:-2]
                if code.endswith('.0'):
                    code = code[:-2]
                
                table_data.append([s_no, enrollment, name, code, password, ''])
                
            t = Table(table_data, colWidths=[1.2*cm, 3.5*cm, 5.5*cm, 2.5*cm, 3.0*cm, 2.8*cm])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E8E8E8')),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0,0), (-1,0), 6),
                ('GRID', (0,0), (-1,-1), 0.8, colors.black),
                ('BOX', (0,0), (-1,-1), 1.5, colors.black),
            ]))
            story.append(t)
            
            if chunk_idx < len(chunks) - 1:
                story.append(PageBreak())

        # Start next room on a new page
        story.append(PageBreak())

    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_master_plan_pdf(allocation, metadata):
    """Generate the Master Seating Plan PDF exactly matching the Seat Allocation system format in-memory"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=15, bottomMargin=20,
        leftMargin=1.2*cm, rightMargin=1.2*cm
    )
    story = []
    styles = getSampleStyleSheet()
    header_style = styles['Heading2']
    header_style.alignment = 1

    dept_name = metadata.get('dept_name', '')
    exam = metadata.get('exam_name', '')
    date_text = metadata.get('date_text', '')
    title = metadata.get('title', 'Master Seating Plan')

    banner = get_banner()
    if banner:
        story.append(banner)
    else:
        story.append(Paragraph(f"<u><b>{dept_name}</b></u>", header_style))

    story.append(Paragraph(f"<b>{exam}</b>", header_style))
    story.append(Paragraph(f"<b>{title}</b>", header_style))
    story.append(Paragraph(f"<b>Date: {date_text}</b>", styles['Normal']))
    story.append(Spacer(1, 0.5*cm))

    # Prepare table headers
    top_header = [
        'S.No', 'Branch', 'Semester', 'Room No.', 'Roll Numbers', '', 'Total', 'Grand Total'
    ]
    sub_header = [
        '', '', '', '', 'From', 'To', '', ''
    ]
    
    table_data = [top_header, sub_header]
    
    total_students = 0
    s_no = 1
    
    for room_data in allocation:
        room_name = room_data['room']
        students = room_data['students']
        if students.empty:
            continue
            
        grand_total = len(students)
        total_students += grand_total
        
        # Get branches (assumes Branch column was added from sheet name)
        if 'BRANCH' in students.columns:
            branches = students['BRANCH'].unique()
        else:
            branches = students['Branch'].unique()
            
        room_rows = []
        for i, branch in enumerate(branches):
            if 'BRANCH' in students.columns:
                branch_students = students[students['BRANCH'] == branch]
                enroll_col = 'ENROLLMENT' if 'ENROLLMENT' in branch_students.columns else 'ENROLLMENT NO'
            else:
                branch_students = students[students['Branch'] == branch]
                enroll_col = 'Enrollment'
                
            if branch_students.empty: continue
            
            # Simple sorting
            if enroll_col in branch_students.columns:
                branch_students = branch_students.sort_values(by=enroll_col)
                enrollments = branch_students[enroll_col].tolist()
            else:
                enrollments = []
            
            if not enrollments: continue
            
            first_roll = str(enrollments[0])
            last_roll = str(enrollments[-1])
            total = len(enrollments)
            
            # Check for branch prefix mismatch
            m_first = re.match(r'^([A-Za-z]{4})', first_roll.upper())
            m_last = re.match(r'^([A-Za-z]{4})', last_roll.upper())
            prefix_first = m_first.group(1) if m_first else first_roll[:4].upper()
            prefix_last = m_last.group(1) if m_last else last_roll[:4].upper()
            
            if prefix_first != prefix_last:
                last_roll = "Onwards"
            
            room_rows.append([
                str(s_no) if i==0 else '',
                branch if i==0 else '', # Display branch only on first row of room
                'IV', # Example semester
                str(room_name) if i==0 else '',
                first_roll,
                last_roll,
                str(total),
                str(grand_total) if i==0 else ''
            ])
            
        table_data.extend(room_rows)
        s_no += 1

    table_data.append(['', '', '', '', 'Total', '', str(total_students), ''])

    col_widths = [1.2*cm, 4*cm, 2*cm, 2.5*cm, 3.5*cm, 3.5*cm, 1.5*cm, 2*cm]
    t = Table(table_data, colWidths=col_widths, repeatRows=2)
    t.setStyle(TableStyle([
        ('SPAN', (4,0), (5,0)), # Merge Roll Numbers header
        ('BACKGROUND', (0,0), (-1,1), colors.HexColor('#E8E8E8')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 0.8, colors.black),
        ('BOX', (0,0), (-1,-1), 1.5, colors.black),
    ]))
    story.append(t)
    story.append(Spacer(1, 2*cm))

    # Add signatures
    sig_table = [
        [metadata.get('left_sign_name', ''), metadata.get('right_sign_name', '')],
        [metadata.get('left_sign_title', ''), metadata.get('right_sign_title', '')]
    ]
    st = Table(sig_table, colWidths=[10*cm, 10*cm])
    st.setStyle(TableStyle([
        ('ALIGN', (0,0), (0,-1), 'LEFT'),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold')
    ]))
    story.append(st)

    doc.build(story)
    buffer.seek(0)
    return buffer

def process_file(input_excel_path, rooms_by_sheet, metadata):
    """Analyze input excel and generate room-wise layout out pdf & excel strictly in memory"""
    
    # 1. Read the input students
    input_xl = pd.ExcelFile(input_excel_path)
    
    # 2. Master Plan Generation Logic (Allocator)
    allocation = []
    
    for sheet in input_xl.sheet_names:
        df = input_xl.parse(sheet)
        if df.empty: continue
        
        # Clean column names to ensure consistent extraction
        df.columns = df.columns.str.strip().str.upper()
        df = df.fillna('')
        
        # Forward fill Branch for logic
        df['BRANCH'] = sheet
        
        rooms = rooms_by_sheet.get(sheet, [])
        current_student_idx = 0
        total_students = len(df)
        
        for room in rooms:
            capacity = room['capacity']
            if current_student_idx >= total_students:
                break
            
            end_idx = min(current_student_idx + capacity, total_students)
            room_students = df.iloc[current_student_idx:end_idx].copy()
            
            # Rewrite the index locally exactly starting from 0 for correct output S.No
            room_students.reset_index(drop=True, inplace=True)
            
            allocation.append({
                'room': room['room'],
                'students': room_students,
                'sheet': sheet
            })
            current_student_idx = end_idx

    # 3. Generate In-Memory Output Files
    pdf_attendance = generate_attendance_pdf(allocation, metadata)
    pdf_masterplan = generate_master_plan_pdf(allocation, metadata)

    # Generate Excel Master Plan in memory
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        summary_data = {'Room': [r['room'] for r in allocation], 'Allocated': [len(r['students']) for r in allocation]}
        pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
        
        for room_data in allocation:
            room_name = room_data['room']
            sheet_name = room_name[:31].replace('/', '_').replace('\\', '_')
            
            # Reconstruct original Excel sheet structure preserving S.No dynamically
            df_out = room_data['students'].copy()
            if 'BRANCH' in df_out.columns:
                df_out = df_out.drop(columns=['BRANCH'])
            if 'Branch' in df_out.columns:
                df_out = df_out.drop(columns=['Branch'])
                
            sno_cols = [c for c in df_out.columns if 'S' in str(c).upper() and 'NO' in str(c).upper()]
            if sno_cols:
                df_out[sno_cols[0]] = range(1, len(df_out) + 1)
            else:
                df_out.insert(0, 'S.No.', range(1, len(df_out) + 1))
                
            df_out.to_excel(writer, sheet_name=sheet_name, index=False)

    excel_buffer.seek(0)

    return {
        'attendance_pdf': pdf_attendance,
        'masterplan_pdf': pdf_masterplan,
        'masterplan_excel': excel_buffer
    }
