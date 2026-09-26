import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "bi_mat_quan_ly_may_tho"

# Thư mục lưu trữ ảnh/video tạm thời
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Khởi tạo cơ sở dữ liệu SQLite (Có thêm cột created_at lưu ngày giờ)
def init_db():
    conn = sqlite3.connect('maintenance.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            engineer TEXT,
            department TEXT,
            model TEXT,
            serial TEXT,
            notes TEXT,
            has_replacement INTEGER,
            parts_name TEXT,
            parts_qty TEXT,
            parts_reason TEXT,
            media_list TEXT,
            status TEXT,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Danh sách 44 máy thở chuẩn hóa
MACHINES_DATA = [
    # ICU Khu B
    {"department": "ICU Khu B", "model": "PB980", "serial": "35B1701595"},
    {"department": "ICU Khu B", "model": "PB840", "serial": "3512201164"},
    {"department": "ICU Khu B", "model": "PB840", "serial": "3512201151"},
    {"department": "ICU Khu B", "model": "PB980", "serial": "35B2005876"},
    {"department": "ICU Khu B", "model": "PB980", "serial": "35B2005879"},
    {"department": "ICU Khu B", "model": "PB980", "serial": "35B2104680"},
    {"department": "ICU Khu B", "model": "PB840", "serial": "3512201144"},
    {"department": "ICU Khu B", "model": "PB980", "serial": "35B2104496"},
    {"department": "ICU Khu B", "model": "PB980", "serial": "35B2104459"},
    {"department": "ICU Khu B", "model": "PB840", "serial": "35B2005882"},
    {"department": "ICU Khu B", "model": "PB840", "serial": "35B2005880"},
    # Nhiệt Đới
    {"department": "Nhiệt Đới", "model": "PB840", "serial": "3512210776"},
    {"department": "Nhiệt Đới", "model": "PB840", "serial": "3512211171"},
    {"department": "Nhiệt Đới", "model": "PB560", "serial": "4096600895"},
    {"department": "Nhiệt Đới", "model": "PB560", "serial": "4096600896"},
    # HS Ngoại TK
    {"department": "HS Ngoại TK", "model": "PB560", "serial": "4096600905"},
    {"department": "HS Ngoại TK", "model": "PB840", "serial": "3512211582"},
    {"department": "HS Ngoại TK", "model": "PB840", "serial": "3512211576"},
    {"department": "HS Ngoại TK", "model": "PB840", "serial": "3512211573"},
    {"department": "HS Ngoại TK", "model": "PB840", "serial": "3512211561"},
    {"department": "HS Ngoại TK", "model": "PB840", "serial": "3512211564"},
    {"department": "HS Ngoại TK", "model": "PB840", "serial": "3512211559"},
    {"department": "HS Ngoại TK", "model": "PB840", "serial": "3512211555"},
    {"department": "HS Ngoại TK", "model": "PB840", "serial": "3512211547"},
    {"department": "HS Ngoại TK", "model": "PB840", "serial": "3512211565"},
    # PTT Người Lớn
    {"department": "PTT Người Lớn", "model": "PB840", "serial": "3512152876"},
    {"department": "PTT Người Lớn", "model": "PB840", "serial": "3512152565"},
    {"department": "PTT Người Lớn", "model": "PB840", "serial": "3512152616"},
    {"department": "PTT Người Lớn", "model": "PB980", "serial": "35B2104679"},
    {"department": "PTT Người Lớn", "model": "PB980", "serial": "35B2104677"},
    {"department": "PTT Người Lớn", "model": "PB840", "serial": "3512152898"},
    # ICU Khu D
    {"department": "ICU Khu D", "model": "PB840", "serial": "3512201145"},
    {"department": "ICU Khu D", "model": "PB840", "serial": "3512201156"},
    {"department": "ICU Khu D", "model": "PB840", "serial": "3512201160"},
    {"department": "ICU Khu D", "model": "PB840", "serial": "3512191966"},
    {"department": "ICU Khu D", "model": "PB840", "serial": "3512152874"},
    {"department": "ICU Khu D", "model": "PB840", "serial": "3512152885"},
    {"department": "ICU Khu D", "model": "PB840", "serial": "3512202941"},
    # PTT Trẻ Em
    {"department": "PTT Trẻ Em", "model": "PB980", "serial": "35B2104673"},
    {"department": "PTT Trẻ Em", "model": "PB980", "serial": "35B2104657"},
    {"department": "PTT Trẻ Em", "model": "PB980", "serial": "35B1401604"},
    {"department": "PTT Trẻ Em", "model": "PB980", "serial": "35B1401531"},
    {"department": "PTT Trẻ Em", "model": "PB980", "serial": "35B2104615"},
    {"department": "PTT Trẻ Em", "model": "PB980", "serial": "35B2104648"}
]

@app.route('/')
def index():
    conn = sqlite3.connect('maintenance.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM reports ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()

    reports_list = []
    for r in rows:
        media_str = r['media_list']
        media_files = media_str.split(',') if media_str else []
        reports_list.append({
            "id": r['id'],
            "engineer": r['engineer'],
            "department": r['department'],
            "model": r['model'],
            "serial": r['serial'],
            "notes": r['notes'],
            "has_replacement": bool(r['has_replacement']),
            "parts_name": r['parts_name'],
            "parts_qty": r['parts_qty'],
            "parts_reason": r['parts_reason'],
            "media_list": [m for m in media_files if m],
            "status": r['status'],
            "created_at": r['created_at'] or "N/A"
        })

    return render_template('index.html', machines=MACHINES_DATA, reports=reports_list)

@app.route('/submit', methods=['POST'])
def submit_inspection():
    engineer_name = request.form.get('engineer_name')
    machine_info = request.form.get('machine_serial')
    notes = request.form.get('notes')
    has_replacement = 1 if request.form.get('has_replacement') == 'on' else 0
    
    parts_name = request.form.get('parts_name', '')
    parts_qty = request.form.get('parts_qty', '')
    parts_reason = request.form.get('parts_reason', '')

    # Lấy ngày giờ hiện tại theo định dạng Việt Nam (DD/MM/YYYY HH:MM)
    created_at = datetime.now().strftime('%d/%m/%Y %H:%M')

    media_filenames = []
    files = request.files.getlist('media_files')
    for file in files:
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            media_filenames.append(filename)

    media_str = ",".join(media_filenames)

    parts = machine_info.split(' | ')
    dept = parts[0] if len(parts) > 0 else ""
    model = parts[1] if len(parts) > 1 else ""
    serial = parts[2] if len(parts) > 2 else ""

    status = "Chờ duyệt xuất kho" if has_replacement == 1 else "Đã hoàn thành kiểm tra"

    conn = sqlite3.connect('maintenance.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO reports (engineer, department, model, serial, notes, has_replacement, parts_name, parts_qty, parts_reason, media_list, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (engineer_name, dept, model, serial, notes, has_replacement, parts_name, parts_qty, parts_reason, media_str, status, created_at))
    conn.commit()
    conn.close()

    flash("Đã tạo biên bản thành công!", "success")
    return redirect(url_for('index'))

@app.route('/approve/<int:report_id>')
def approve_report(report_id):
    conn = sqlite3.connect('maintenance.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE reports SET status = ? WHERE id = ?', ("Đã duyệt xuất kho & Hoàn tất", report_id))
    conn.commit()
    conn.close()

    flash(f"Đã duyệt xuất kho cho biên bản #{report_id}!", "success")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=port)