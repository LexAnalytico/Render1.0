from flask import Flask, request, render_template_string, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecret'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_type(filename):
    ext = filename.rsplit('.', 1)[1].lower()
    return 'PDF' if ext == 'pdf' else 'Image'

# ===== HTML TEMPLATES (Embedded in Python) =====
UPLOAD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Document Upload</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        form { max-width: 500px; margin: auto; }
        select, input[type="file"] { width: 100%; padding: 8px; margin: 5px 0; }
        input[type="submit"] { background: #4CAF50; color: white; border: none; padding: 10px; cursor: pointer; }
        .error { color: red; }
    </style>
</head>
<body>
    <h2>Upload Document</h2>
    <form method="POST" action="/upload" enctype="multipart/form-data">
        <label for="doc_type">Document Type:</label>
        <select id="doc_type" name="doc_type" required>
            <option value="" disabled selected>Select document type</option>
            <option value="Invoice">Invoice</option>
            <option value="Warranty">Warranty</option>
            <option value="Extended Warranty">Extended Warranty</option>
        </select><br><br>
        
        <label for="file_type">Expected File Type:</label>
        <select id="file_type" name="file_type" required>
            <option value="" disabled selected>Select file type</option>
            <option value="PDF">PDF</option>
            <option value="Image">Image</option>
        </select><br><br>
        
        <label>Upload File:</label>
        <input type="file" name="file" accept=".pdf,.png,.jpg,.jpeg,.gif" required><br><br>
        
        <input type="submit" value="Upload">
    </form>
    
    {% with messages = get_flashed_messages() %}
        {% if messages %}
            <ul class="error">
                {% for msg in messages %}
                    <li>{{ msg }}</li>
                {% endfor %}
            </ul>
        {% endif %}
    {% endwith %}
</body>
</html>
"""

RESULT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Upload Result</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .verified { color: green; font-weight: bold; }
        .not-verified { color: red; font-weight: bold; }
        .result-box { max-width: 500px; margin: auto; border: 1px solid #ddd; padding: 20px; }
        a { display: inline-block; margin-top: 20px; color: #4CAF50; }
    </style>
</head>
<body>
    <div class="result-box">
        <h2>Document Verification Result</h2>
        
        <p><strong>Document Type:</strong> {{ doc_type }}</p>
        <p><strong>Expected File Type:</strong> {{ expected_type }}</p>
        <p><strong>Actual File Type:</strong> {{ actual_type }}</p>
        <p><strong>Filename:</strong> {{ filename }}</p>
        
        <p><strong>Status:</strong> 
            <span class="{% if is_verified %}verified{% else %}not-verified{% endif %}">
                {% if is_verified %}VERIFIED ✅{% else %}NOT VERIFIED ❌{% endif %}
            </span>
        </p>
        
        <a href="/">Upload another document</a>
    </div>
</body>
</html>
"""

# ===== ROUTES =====
@app.route('/')
def index():
    return render_template_string(UPLOAD_TEMPLATE)

@app.route('/upload', methods=['POST'])
def upload_file():
    doc_type = request.form.get('doc_type')
    expected_file_type = request.form.get('file_type')
    
    if 'file' not in request.files:
        flash('No file selected!')
        return redirect('/')
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No file selected!')
        return redirect('/')
    
    if not allowed_file(file.filename):
        flash('Only PDF, PNG, JPG, JPEG, GIF files allowed!')
        return redirect('/')
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    actual_file_type = get_file_type(filename)
    is_verified = (expected_file_type == actual_file_type)
    
    return render_template_string(RESULT_TEMPLATE,
                                doc_type=doc_type,
                                expected_type=expected_file_type,
                                actual_type=actual_file_type,
                                filename=filename,
                                is_verified=is_verified)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)), debug=False)
