from flask import Flask, request, render_template_string, send_file, flash, redirect, url_for, abort
import os
import io
import traceback
import pandas as pd
from werkzeug.utils import secure_filename
from generator import process_file

app = Flask(__name__)
app.secret_key = "super_secret_key"

# In-memory session-like store for downloaded files
IN_MEMORY_FILES = {}

COMMON_HEAD = """
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #4f46e5;
            --primary-hover: #4338ca;
            --primary-light: #e0e7ff;
            --success: #10b981;
            --success-hover: #059669;
            --bg-color: #f3f4f6;
            --card-bg: #ffffff;
            --text-main: #1f2937;
            --text-muted: #6b7280;
            --border-color: #e5e7eb;
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
            --border-radius: 12px;
        }

        * { font-family: 'Inter', sans-serif; box-sizing: border-box; }
        
        body { 
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            color: var(--text-main);
            margin: 0;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2rem 1rem;
        }
        
        .container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: var(--border-radius);
            box-shadow: var(--shadow-xl);
            padding: 2.5rem;
            width: 100%;
            max-width: 650px;
            transition: all 0.3s ease;
            border: 1px solid rgba(255,255,255,0.4);
            position: relative;
        }
        
        .container.wide {
            max-width: 1100px;
            margin: auto;
        }

        h1 { color: var(--primary); font-weight: 700; text-align: center; margin-top: 0; margin-bottom: 2rem; font-size: 2.2rem; }
        h2 { color: var(--text-main); font-weight: 600; font-size: 1.5rem; margin-bottom: 1.5rem; border-bottom: 2px solid var(--border-color); padding-bottom: 0.5rem; }
        h3 { color: var(--text-main); font-size: 1.2rem; margin-top: 0; }

        form { display: flex; flex-direction: column; gap: 1.2rem; }
        label { font-weight: 500; color: var(--text-main); font-size: 0.95rem; margin-bottom: 0.3rem; display: block; }
        p.help-text { margin: -0.8rem 0 0.5rem 0; font-size: 0.8rem; color: var(--text-muted); }
        
        input[type="text"], input[type="number"], input[type="file"], textarea, select {
            width: 100%; padding: 0.8rem 1rem; border: 1.5px solid var(--border-color);
            border-radius: 8px; font-family: 'Inter', sans-serif; font-size: 0.95rem;
            transition: all 0.3s ease; background-color: #fafbfc;
        }
        
        input[type="text"]:focus, input[type="number"]:focus, textarea:focus, select:focus { 
            border-color: var(--primary); outline: none; background-color: #fff; box-shadow: 0 0 0 4px var(--primary-light); 
        }

        button {
            background: linear-gradient(135deg, var(--primary) 0%, #312e81 100%);
            color: white; padding: 1rem 1.5rem; border: none; border-radius: 8px;
            font-weight: 600; cursor: pointer; font-size: 1rem; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 6px rgba(79, 70, 229, 0.25); letter-spacing: 0.5px;
        }
        button:hover { transform: translateY(-2px); box-shadow: 0 8px 15px rgba(79, 70, 229, 0.3); }
        
        .messages { background: var(--primary-light); color: var(--primary-hover); padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem; border-left: 4px solid var(--primary); font-weight: 500;}

        /* Preview Cards Grid */
        .cards-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 1.25rem; margin-bottom: 2.5rem; }
        .sheet-card {
            background: rgba(255,255,255,0.8); border: 1px solid var(--border-color);
            border-radius: var(--border-radius); padding: 1.2rem;
            position: relative; transition: all 0.3s ease;
            display: flex; flex-direction: column; justify-content: space-between;
        }
        .sheet-card:hover { box-shadow: var(--shadow-md); transform: translateY(-2px); background: #ffffff; }
        .sheet-title { font-weight: 600; color: var(--primary); margin: 0 0 0.5rem 0; word-break: break-all; font-size: 1.1rem; border-bottom: none;}
        .sheet-summary { font-size: 0.85rem; color: var(--text-muted); margin-bottom: 1rem; }

        .eye-btn {
            align-self: flex-start; background: var(--primary-light); border: none; border-radius: 50%; 
            width: 38px; height: 38px; display: flex; align-items: center; justify-content: center; 
            cursor: pointer; color: var(--primary); transition: all 0.2s; position: relative;
        }
        .eye-btn:hover { background: var(--primary); color: white; transform: scale(1.05); }

        /* Tooltip style */
        .eye-btn .tooltip {
            visibility: hidden; opacity: 0; position: absolute; top: -10px; left: 115%; background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px); border: 1px solid var(--primary-light); border-radius: 8px;
            box-shadow: var(--shadow-xl); padding: 0.5rem 0.8rem; z-index: 100; transition: all 0.3s ease; 
            transform: translateX(-10px); width: max-content; font-size: 0.8rem; font-weight: 600; color: var(--text-main);
        }
        .eye-btn:hover .tooltip { visibility: visible; opacity: 1; transform: translateX(0); }

        /* Glass Modal Overlay */
        .modal-overlay {
            position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(15, 23, 42, 0.6); 
            backdrop-filter: blur(12px); display: flex; align-items: center; justify-content: center; 
            z-index: 1000; opacity: 0; visibility: hidden; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .modal-overlay.active { opacity: 1; visibility: visible; }
        .modal-content {
            background: rgba(255,255,255,0.95); backdrop-filter: blur(20px); border-radius: 16px; 
            border: 1px solid rgba(255,255,255,0.5); padding: 2.5rem; max-width: 900px; width: 90%; 
            max-height: 85vh; overflow-y: auto; box-shadow: var(--shadow-xl); transform: scale(0.95) translateY(20px); 
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1); position: relative;
        }
        .modal-overlay.active .modal-content { transform: scale(1) translateY(0); }
        .modal-close {
            position: absolute; top: 1.5rem; right: 1.5rem; background: #f1f5f9; border: none; 
            border-radius: 50%; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center;
            font-size: 1.2rem; cursor: pointer; color: var(--text-muted); transition: all 0.2s;
        }
        .modal-close:hover { background: #fee2e2; color: #ef4444; transform: rotate(90deg);}

        table { border-collapse: separate; border-spacing: 0; width: 100%; border: 1px solid var(--border-color); border-radius: 8px; overflow: hidden; margin-bottom: 1rem;}
        th, td { padding: 0.75rem 1rem; border-bottom: 1px solid var(--border-color); text-align: left;}
        th { background: #f8fafc; font-weight: 600; color: var(--text-muted); text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.05em;}
        tr:last-child td { border-bottom: none; }
        tbody tr:hover { background-color: var(--primary-light); }

        .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; }
        .form-group.full { grid-column: span 2; }

        /* Dynamic Room Configuration UI */
        .branch-adder {
            display: flex; gap: 1rem; align-items: flex-end; margin-bottom: 1.5rem;
            background: #fff; padding: 1.5rem; border-radius: var(--border-radius); border: 1px dashed var(--primary);
        }
        .branch-adder .form-group { margin-bottom: 0; flex: 1; }
        .branch-adder button { margin-top: 0; background: var(--primary-light); color: var(--primary-hover); box-shadow: none;}
        .branch-adder button:hover { background: var(--primary); color: white; }

        .dynamic-room-config {
            background: #fff; border: 1px solid var(--border-color); padding: 1.5rem; border-radius: var(--border-radius);
            margin-bottom: 1.5rem; box-shadow: var(--shadow-md); position: relative; overflow: hidden;
        }
        .dynamic-room-config::before { content:''; position: absolute; left: 0; top: 0; bottom: 0; width: 4px; background: var(--success); }
        .room-row { display: flex; gap: 1rem; margin-top: 0.8rem; align-items: center; }
        .room-row input { flex: 1; }

        /* Backlink & Downloads */
        .downloads { display: flex; flex-direction: column; gap: 1rem; margin-top: 1.5rem; }
        .download-btn {
            background: linear-gradient(135deg, var(--success) 0%, #047857 100%);
            color: white; text-decoration: none; padding: 1.1rem; border-radius: 8px; font-weight: 600;
            box-shadow: 0 4px 6px rgba(16, 185, 129, 0.25); transition: all 0.3s ease; text-align: center;
        }
        .download-btn:hover { transform: translateY(-2px); box-shadow: 0 8px 15px rgba(16, 185, 129, 0.3); color: white; }
        .back-link { display: inline-block; margin-top: 2rem; color: var(--primary); text-decoration: none; font-weight: 500; font-size: 1rem; transition: color 0.2s;}
        .back-link:hover { color: var(--primary-hover); text-decoration: underline; }
    </style>
"""

HTML_UPLOAD = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Upload Master Plan</title>
    {COMMON_HEAD}
</head>
<body>
    <div class="container">
        <h1>Master Plan Tool</h1>
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            <div class="messages">
              {% for message in messages %}
                <p>{{ message }}</p>
              {% endfor %}
            </div>
          {% endif %}
        {% endwith %}
        <form method="POST" enctype="multipart/form-data" action="/">
            <div>
                <label for="input_file">Input Students Excel File (.xlsx)</label>
                <p class="help-text">e.g., Department of CSE IV Sem.xlsx</p>
                <input type="file" name="input_file" id="input_file" accept=".xlsx" required>
            </div>
            <button type="submit">Upload and Extract Data</button>
        </form>
    </div>
</body>
</html>
""".replace("{COMMON_HEAD}", COMMON_HEAD)

HTML_PREVIEW = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Configure Master Plan</title>
    {COMMON_HEAD}
</head>
<body>
    <div class="container wide">
        <h1>Data Preview & Room Allocation</h1>
        
        <h2>Preview Extracted Sheets</h2>
        <div class="cards-grid">
            {% for sheet_name, data in preview_data.items() %}
                <div class="sheet-card">
                    <div>
                        <h3 class="sheet-title">{{ sheet_name }}</h3>
                        <div class="sheet-summary">Students: <strong>{{ data.total }}</strong> extracted</div>
                    </div>
                    <button type="button" class="eye-btn" onclick="openModal('{{ sheet_name|replace(' ', '')|replace('&', '') }}', '{{ sheet_name }}')">
                        <!-- Eye SVG -->
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
                        
                        <div class="tooltip" onclick="event.stopPropagation();">
                            View First 10 Rows
                        </div>
                    </button>

                    <!-- Hidden element holding table structure for Modal injection -->
                    <div id="tableContent_{{ sheet_name|replace(' ', '')|replace('&', '') }}" style="display:none;">
                        {{ data.html|safe }}
                    </div>
                </div>
            {% endfor %}
        </div>

        <h2>Room & PDF Configuration Station</h2>
        <form method="POST" action="/generate" id="generateForm">
            <input type="hidden" name="file_id" value="{{ file_id }}">
            <textarea name="rooms_config" id="hidden_rooms_config" style="display:none;"></textarea>
            
            <div class="branch-adder">
                <div class="form-group">
                    <label>Select Branch to Allocate Rooms</label>
                    <select id="new-branch-select">
                        <option value="" disabled selected>-- Choose Branch --</option>
                        {% for sheet_name in preview_data.keys() %}
                            <option value="{{ sheet_name }}">{{ sheet_name }}</option>
                        {% endfor %}
                    </select>
                </div>
                <button type="button" onclick="addBranchConfig()">+ Add Branch Config</button>
            </div>

            <div id="branch-configs-container">
                <!-- JS will populate Dynamic Room configuration panels here -->
            </div>
            
            <h2 style="margin-top: 2rem;">General PDF Metadata</h2>
            <div class="form-grid">
                <div class="form-group full">
                    <label>Department Name</label>
                    <input type="text" name="dept_name" value="Department of Computer Science & Engineering" required>
                </div>
                <div class="form-group">
                    <label>Exam Name</label>
                    <input type="text" name="exam_name" value="IV Sem Quiz" required>
                </div>
                <div class="form-group">
                    <label>Date</label>
                    <input type="text" name="date_text" value="08.04.2026" required>
                </div>
                <div class="form-group full">
                    <label>Title</label>
                    <input type="text" name="title" value="Master Seating Plan" required>
                </div>
                
                <div class="form-group">
                    <label>Left Signature Name</label>
                    <input type="text" name="left_sign_name" value="Exam Coordinator">
                </div>
                <div class="form-group">
                    <label>Left Signature Title</label>
                    <input type="text" name="left_sign_title" value="Department of CSE">
                </div>
                <div class="form-group">
                    <label>Right Signature Name</label>
                    <input type="text" name="right_sign_name" value="HOD">
                </div>
                <div class="form-group">
                    <label>Right Signature Title</label>
                    <input type="text" name="right_sign_title" value="Department of CSE">
                </div>
                
                <div class="form-group full">
                    <button type="button" class="full" style="width: 100%; border-radius: 12px; padding: 1.2rem; font-size: 1.1rem; box-shadow: var(--shadow-lg);" onclick="submitForm()">✨ Generate Master Plan & Attendance File</button>
                </div>
            </div>
        </form>
    </div>

    <!-- Glassmorphism Modal Overlay -->
    <div class="modal-overlay" id="glassModal" onclick="closeModal()">
        <div class="modal-content" onclick="event.stopPropagation()">
            <button class="modal-close" onclick="closeModal()">✕</button>
            <h2 id="modalTitle" style="color: var(--primary); margin-top: 0; padding-right: 2rem;">Sheet Preview</h2>
            <div id="modalTableContainer" style="overflow-x: auto; margin-top: 1.5rem;">
                <!-- Table injected here via JS -->
            </div>
        </div>
    </div>

    <script>
        // --- Modal Logic ---
        function openModal(idId, sheetName) {
            document.getElementById('modalTitle').innerText = sheetName + " (First 10 Data Rows)";
            const content = document.getElementById('tableContent_' + idId).innerHTML;
            document.getElementById('modalTableContainer').innerHTML = content;
            document.getElementById('glassModal').classList.add('active');
        }
        function closeModal() {
            document.getElementById('glassModal').classList.remove('active');
        }

        // --- Dynamic Room Configurator logic ---
        let branchConfigs = {};

        function addBranchConfig() {
            const select = document.getElementById('new-branch-select');
            const branch = select.value;
            if (!branch) return;
            if (!branchConfigs[branch]) {
                branchConfigs[branch] = { rooms: [{name: '', capacity: ''}] };
                renderBranchConfigs();
            }
        }

        function removeBranch(branch) {
            delete branchConfigs[branch];
            renderBranchConfigs();
        }

        function updateRoomCount(branch, countElement) {
            let cnt = parseInt(countElement.value) || 1;
            let rooms = branchConfigs[branch].rooms;
            while (rooms.length < cnt) rooms.push({name: '', capacity: ''});
            while (rooms.length > cnt) rooms.pop();
            renderBranchConfigs();
        }

        function syncTextarea() {
            let text = '';
            for (let b in branchConfigs) {
                text += `[${b}]\\n`;
                const blocks = document.querySelectorAll(`.room-row[data-branch="${b}"]`);
                blocks.forEach(block => {
                    const rName = block.querySelector('.r-name').value;
                    const rCap = block.querySelector('.r-cap').value || 0;
                    if(rName.trim()) {
                        text += `${rName}=${rCap}\\n`;
                    }
                });
                text += `\\n`;
            }
            document.getElementById('hidden_rooms_config').value = text.trim();
        }

        function renderBranchConfigs() {
            const container = document.getElementById('branch-configs-container');
            container.innerHTML = '';
            
            for (let branch in branchConfigs) {
                let config = branchConfigs[branch];
                
                let html = `
                <div class="dynamic-room-config">
                    <div style="display:flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); padding-bottom: 0.8rem; margin-bottom: 1.2rem;">
                        <h3 style="margin:0; color: var(--text-main); font-size: 1.1rem;">Branch Configuration: <strong>${branch}</strong></h3>
                        <button type="button" onclick="removeBranch('${branch}')" style="margin:0; padding: 0.5rem 1rem; background: #fee2e2; color: #ef4444; width: auto; font-size: 0.85rem;">Remove</button>
                    </div>
                    <div class="form-group" style="margin-bottom: 1.5rem; max-width: 250px;">
                        <label>Number of Rooms</label>
                        <input type="number" min="1" max="50" value="${config.rooms.length}" onchange="updateRoomCount('${branch}', this)">
                    </div>
                    
                    <div style="display: flex; gap: 1rem; margin-bottom: 0.5rem;">
                        <div style="flex: 1; font-size: 0.8rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase;">Room / Lab Name</div>
                        <div style="flex: 1; font-size: 0.8rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase;">Room Capacity</div>
                    </div>
                `;
                
                for (let i = 0; i < config.rooms.length; i++) {
                    let r = config.rooms[i];
                    html += `
                    <div class="room-row" data-branch="${branch}" data-idx="${i}">
                        <input type="text" class="r-name" placeholder="e.g. Lab 104" value="${r.name}" oninput="syncTextarea()">
                        <input type="number" class="r-cap" placeholder="e.g. 35" value="${r.capacity}" oninput="syncTextarea()">
                    </div>
                    `;
                }
                html += `</div>`;
                container.innerHTML += html;
            }
            syncTextarea();
        }

        function submitForm() {
            syncTextarea();
            if(document.getElementById('hidden_rooms_config').value.trim() === '') {
                alert("Please add at least one branch and room configuration!");
                return;
            }
            document.getElementById('generateForm').submit();
        }
    </script>
</body>
</html>
""".replace("{COMMON_HEAD}", COMMON_HEAD)

HTML_RESULT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Generation Complete</title>
    {COMMON_HEAD}
</head>
<body>
    <div class="container" style="text-align: center;">
        <h1>Generation Successful!</h1>
        <p style="color: var(--text-muted); margin-bottom: 2rem;">Your PDF and Excel files have been generated entirely in-memory and are ready for download.</p>
        <div class="downloads">
            <a class="download-btn" href="/download/Attendance_Generated.pdf">⬇ Download Attendance Sheets (PDF)</a>
            <a class="download-btn" href="/download/Master_Plan_Generated.pdf">⬇ Download Master Plan (PDF)</a>
            <a class="download-btn" href="/download/Master_Plan_Generated.xlsx">⬇ Download Master Plan (Excel)</a>
        </div>
        <a class="back-link" href="/">&larr; Back to Upload Station</a>
    </div>
</body>
</html>
""".replace("{COMMON_HEAD}", COMMON_HEAD)

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'input_file' not in request.files:
            flash('Input file is required.')
            return redirect(url_for('index'))
            
        input_file = request.files['input_file']
        if input_file.filename == '':
            flash('No selected file')
            return redirect(url_for('index'))
            
        try:
            # Safe parsing
            file_data = input_file.read()
            in_memory_xl = io.BytesIO(file_data)
            
            # Store it in memory for generating
            import uuid
            file_id = str(uuid.uuid4())
            IN_MEMORY_FILES[file_id] = file_data
            
            # Parse excel and create preview
            preview_data = {}
            xl = pd.ExcelFile(in_memory_xl)
            for sheet in xl.sheet_names:
                df = xl.parse(sheet)
                if df.empty: continue
                total = len(df)
                df_subset = df.head(10).fillna('')
                preview_data[sheet] = {
                    'total': total,
                    'html': df_subset.to_html(index=False, classes="table table-striped table-hover")
                }
                
            return render_template_string(HTML_PREVIEW, preview_data=preview_data, file_id=file_id)
            
        except Exception as e:
            flash(f"Error during processing: {str(e)}")
            print(traceback.format_exc())
            return redirect(url_for('index'))

    return render_template_string(HTML_UPLOAD)

@app.route("/generate", methods=['POST'])
def generate():
    try:
        file_id = request.form.get('file_id')
        if file_id not in IN_MEMORY_FILES:
            return "File session expired. Please process again."
            
        in_memory_xl = io.BytesIO(IN_MEMORY_FILES[file_id])
        
        # Parse inputs
        rooms_config = request.form.get('rooms_config', '')
        metadata = {
            'dept_name': request.form.get('dept_name', ''),
            'exam_name': request.form.get('exam_name', ''),
            'date_text': request.form.get('date_text', ''),
            'title': request.form.get('title', ''),
            'left_sign_name': request.form.get('left_sign_name', ''),
            'left_sign_title': request.form.get('left_sign_title', ''),
            'right_sign_name': request.form.get('right_sign_name', ''),
            'right_sign_title': request.form.get('right_sign_title', '')
        }
        
        rooms_by_sheet = {}
        current_sheet = None
        for line in rooms_config.split('\n'):
            line = line.strip()
            if not line: continue
            if line.startswith('[') and line.endswith(']'):
                current_sheet = line[1:-1].strip()
                rooms_by_sheet[current_sheet] = []
            elif '=' in line and current_sheet is not None:
                room_name, cap = line.split('=', 1)
                try:
                    rooms_by_sheet[current_sheet].append({'room': room_name.strip(), 'capacity': int(cap.strip())})
                except ValueError:
                    pass
                    
        # Generate with in-memory buffer
        results = process_file(in_memory_xl, rooms_by_sheet, metadata)
        
        # Free up the input memory and replace with generated outputs
        del IN_MEMORY_FILES[file_id]
        
        IN_MEMORY_FILES['Attendance_Generated.pdf'] = results['attendance_pdf'].read()
        IN_MEMORY_FILES['Master_Plan_Generated.pdf'] = results['masterplan_pdf'].read()
        IN_MEMORY_FILES['Master_Plan_Generated.xlsx'] = results['masterplan_excel'].read()
        
        return render_template_string(HTML_RESULT)
        
    except Exception as e:
        print(traceback.format_exc())
        return f"Error during generation: {str(e)}"

@app.route("/download/<filename>")
def download(filename):
    if filename not in IN_MEMORY_FILES:
        abort(404)
        
    file_bytes = io.BytesIO(IN_MEMORY_FILES[filename])
    
    if filename.endswith('.pdf'):
        mimetype = 'application/pdf'
    else:
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        
    return send_file(file_bytes, as_attachment=True, download_name=filename, mimetype=mimetype)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
