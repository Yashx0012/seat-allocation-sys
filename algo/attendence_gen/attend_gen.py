import json
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm

# --- CONFIGURATION ---
IMAGE_PATH = "/home/blazex/Documents/git/seat-allocation-sys/algo/attendence_gen/data/banner.png"
CACHE_DIR = "../cache" 

def header_and_footer(c, doc, room_no):
    """Restored your exact original header/footer logic"""
    c.saveState()
    page_width, page_height = A4
    BANNER_HEIGHT = 3.2 * cm
    CONTENT_WIDTH = page_width - doc.leftMargin - doc.rightMargin 
    
    try:
        c.drawImage(IMAGE_PATH,
                    x=doc.leftMargin - 0.8*cm,
                    y=page_height - doc.topMargin - 0.3* cm,
                    width=CONTENT_WIDTH +50,
                    height=BANNER_HEIGHT ,
                    preserveAspectRatio=True)
    except Exception:
        c.setFont('Times-Bold', 12)
        c.drawCentredString(page_width / 2, page_height - 2*cm, "Header Image Missing")

    room_box_width = 3.1 * cm
    room_box_height = 0.65 * cm
    c.rect(page_width - doc.rightMargin - room_box_width + 14, 
           page_height - 0.98 * cm, 
           room_box_width, room_box_height)
    
    c.setFont('Times-Roman', 10)
    c.drawString(page_width - doc.rightMargin - room_box_width + 17, 
                 page_height - 0.8 * cm, f"Room No. {room_no}")
    c.restoreState()

def create_attendance_pdf(filename, student_list, batch_label, metadata, extracted_info):
    """Your original PDF layout and table styles - UNCHANGED"""
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        topMargin=3.8 * cm,
        bottomMargin=2.0 * cm,
        leftMargin=1.2 * cm,
        rightMargin=1.2 * cm
    )
    story = []
    styles = getSampleStyleSheet()

    for style in styles.byName.values():
        style.fontName = 'Times-Roman'

    header_style = styles['Normal'].clone('HeaderStyle')
    header_style.alignment = 1 
    
    story.append(Paragraph(f"<u><b>DEPARTMENT OF {batch_label}</b></u>", header_style))
    story.append(Spacer(1, 0.1*cm))
    
    degree = extracted_info.get('degree', 'B.Tech')
    branch = extracted_info.get('branch', 'N/A')
    joining_year = extracted_info.get('joining_year', '2024')
    current_year = metadata.get('year', '2025')
    
    story.append(Paragraph(
        f"<b>{degree} ({branch}), Batch - {joining_year}, Year {current_year}</b>", 
        header_style
    ))
    
    title_style = styles['Normal'].clone('TitleStyle')
    title_style.alignment = 1
    title_style.textColor = colors.darkgreen
    exam_title = metadata.get('exam_title', 'EXAMINATION-ATTENDANCE SHEET')
    story.append(Paragraph(f"<b>{exam_title}</b>", title_style))
    story.append(Spacer(1, 0.3*cm))

    info_style = styles['Normal'].clone('InfoStyle')
    info_data = [
        [Paragraph(f"<b>Course Name :- {metadata.get('course_name', 'N/A')}</b>", info_style), 
         Paragraph(f"<b>Course Code :- {metadata.get('course_code', 'N/A')}</b>", info_style)],
        [Paragraph(f"<b>Date :- {metadata.get('date', '')}</b>", info_style), 
         Paragraph(f"<b>Time :- {metadata.get('time', '')}</b>", info_style)]
    ]
    info_table = Table(info_data, colWidths=[10*cm, 8.5*cm])
    info_table.setStyle(TableStyle([
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('FONTNAME', (0,0), (-1,-1), 'Times-Roman')
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.3*cm))

    table_headers = ["S. No.", "Name of the Student", "Enrolment No.", "Set A/ Set B", "Answer Booklet No.", "Signature"]
    data = [table_headers]

    for i, student in enumerate(student_list):
        data.append([
            str(i + 1),
            student.get('student_name',''), 
            student.get('roll_number', ''),
            student.get('paper_set', ''),
            "DU                           ",
            ""
        ])

    col_widths = [1.3*cm, 5.5*cm, 3.6*cm, 2.4*cm, 3.6*cm, 3.1*cm]
    total_table_width = sum(col_widths)

    attendance_table = Table(data, colWidths=col_widths, repeatRows=1)
    attendance_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 0), (-1, -1), 10), 
        ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
        ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),
    ]))
    story.append(attendance_table)

    summary_data = [
        [Paragraph(f"<b>No. of Students Registered = {len(student_list)}</b>", info_style)],
        [Paragraph("<b>No. of Students Appeared =</b>", info_style)],
        [Paragraph("<b>No. of Students Absent =</b>", info_style)],
        [Paragraph("<b>No. of Students Detained =</b>", info_style)]
    ]
    summary_table = Table(summary_data, colWidths=[total_table_width])
    summary_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.8, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('FONTNAME', (0,0), (-1,-1), 'Times-Roman')
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 1.7 * cm))
    
    sig_style = styles['Normal'].clone('SigStyle')
    sig_data = [[
        Paragraph("<b>1. Signature and Name of invigilator</b>", sig_style),
        Paragraph("<b>2. Signature and Name of invigilator</b>", sig_style)
    ]]
    sig_table = Table(sig_data, colWidths=[total_table_width/1.5, total_table_width/2 - 80])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    story.append(sig_table)

    room_no = metadata.get('room_no', 'N/A')
    doc.build(story, 
              onFirstPage=lambda canvas, doc: header_and_footer(canvas, doc, room_no), 
              onLaterPages=lambda canvas, doc: header_and_footer(canvas, doc, room_no))

def process_and_generate_from_cache(plan_id, frontend_metadata=None):
    """
    CLEANED: Uses the structured 'batches' directly from CacheManager.
    No more regex parsing or manual batching loops here.
    """
    file_path = os.path.join(CACHE_DIR, f"{plan_id}.json")
    if not os.path.exists(file_path): return None

    with open(file_path, 'r') as f:
        json_data = json.load(f)

    # 1. Directly access pre-structured batches
    batches = json_data.get('batches', {})
    inputs = json_data.get('inputs', {})

    # 2. Setup metadata
    metadata = {
        "room_no": inputs.get('room_id', 'Manual'),
        "date": json_data.get('metadata', {}).get('last_updated', '').split('T')[0],
        "course_name": "N/A", "course_code": "N/A", "exam_title": "ATTENDANCE SHEET", "year": "2025"
    }
    if frontend_metadata: metadata.update(frontend_metadata)

    # 3. Print each batch using cached data
    output_files = []
    output_dir = "generated_report"
    os.makedirs(output_dir, exist_ok=True)

    for b_label, b_data in batches.items():
        students = b_data.get('students', [])
        extracted_info = b_data.get('info', {}) # Already parsed by CacheManager!
        
        if students:
            file_name = f"{output_dir}/attendance_{plan_id}_{b_label}.pdf"
            create_attendance_pdf(file_name, students, b_label, metadata, extracted_info)
            output_files.append(file_name)
    
    return output_files

if __name__ == '__main__':
    import sys
    process_and_generate_from_cache(sys.argv[1] if len(sys.argv) > 1 else "plan_test")