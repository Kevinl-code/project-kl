from flask import Flask, render_template_string, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os

# Initialize the Flask app
app = Flask(__name__)
app.secret_key = "supersecretkey"
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'xls', 'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Visualization Trends</title>
    <style>
        body {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            padding: 0;
            overflow: hidden;
        }
        .background {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: url("/static/anim2.gif") no-repeat center center fixed;
            background-size: cover;
            z-index: 0;
            opacity: 0.4;
        }
        #typing {
            font-size: 2rem;
            color: blue;
            white-space: nowrap;
            overflow: hidden;
            border-right: 2px solid rgba(210, 210, 231, 0);
            display: inline-block;
            animation: glow 2s infinite alternate;
            z-index: 1;
            position: relative;
        }
        .btn {
            background-color: orange;
            color: white;
            padding: 10px 20px;
            font-size: 1.2rem;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            margin-top: 20px;
            transition: background-color 0.3s ease;
            z-index: 1;
            position: relative;
        }
        .btn:hover {
            background-color: #ff8c00;
        }
        @keyframes glow {
            0% {
                text-shadow: 0 0 1px blue, 0 0 2px purple, 0 0 3px white, 0 0 6px yellow;
            }
            50% {
                text-shadow: 0 0 2px blue, 0 0 3px purple, 0 0 5px white, 0 0 6px yellow;
            }
            100% {
                text-shadow: 0 0 3px blue, 0 0 5px purple, 0 0 6px white, 0 0 9px yellow;
            }
        }
    </style>
</head>
<body>
    <div class="background"></div>
    <div id="typing"></div>
    <button class="btn" onclick="window.location.href='/dashboard'">Get Started</button>
    <script>
        const text = "Comprehensive Data Visualization in Recent Trends of CS";
        const typingElement = document.getElementById('typing');
        let i = 0;
        let typingSpeed = 50;

        function typeText() {
            if (i < text.length) {
                typingElement.innerHTML += text.charAt(i);
                i++;
                setTimeout(typeText, typingSpeed);
            } else {
                setTimeout(resetTyping, 1500);
            }
        }

        function resetTyping() {
            typingElement.innerHTML = "";
            i = 0;
            typeText();
        }

        typeText();
    </script>
</body>
</html>
    ''')

@app.route('/dashboard')
def dashboard():
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard</title>
    <style>
        body {
            display: flex;
            margin: 0;
            padding: 0;
            height: 100vh;
            overflow: hidden;
        }
        .sidebar {
            position: fixed;
            top: 0;
            left: 0;
            width: 250px;
            height: 100%;
            background-color: #343a40;
            color: white;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 1cm;
        }
        .sidebar a {
            color: white;
            text-decoration: none;
            margin: 10px 0;
            padding: 10px;
            border-radius: 5px;
            font-size: 1.6rem;
        }
        .sidebar a:hover {
            background-color: rgb(195, 89, 19);
        }
        .content {
            margin-left: 250px;
            padding: 20px;
            width: calc(100% - 250px);
            background-color: #f5f5f5;
            height: 100%;
        }
    </style>
</head>
<body>
    <div class="sidebar">
        <a href="/import">Import Data</a>
        <a href="#">Category</a>
        <a href="#">Charts</a>
        <a href="#">Export</a>
    </div>
    <div class="content">
        <h2>Welcome to the Data Visualization Dashboard!</h2>
    </div>
</body>
</html>
    ''')

@app.route('/import', methods=['GET', 'POST'])
def import_data():
    filename = None  # Store filename to display dynamically

    if request.method == 'POST':
        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files['file']
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                flash('File uploaded successfully!')

    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Import Data</title>
    <style>
        body {
            display: flex;
            margin: 0;
            padding: 0;
            height: 100vh;
            overflow: hidden;
        }
        .sidebar {
            position: fixed;
            top: 0;
            left: 0;
            width: 250px;
            height: 100%;
            background-color: #343a40;
            color: white;
            padding: 0px;
            display: flex;
            flex-direction: column;
            gap: 1cm;
        }
        .sidebar a {
            color: white;
            text-decoration: none;
            margin: 10px 0;
            padding: 10px;
            border-radius: 5px;
            font-size: 1.6rem;
        }
        .sidebar a:hover {
            background-color: rgb(195, 89, 19);
        }
        .content {
            margin-left: 250px;
            padding: 20px;
            width: calc(100% - 250px);
            background-color: #f5f5f5;
            height: 100%;
        }
        .file-input {
            margin: 20px 0;
        }
        .file-input label {
            display: inline-block;
            padding: 10px 20px;
            background-color: orange;
            color: white;
            border-radius: 5px;
            cursor: pointer;
        }
        .file-input input {
            display: none;
        }
        .file-name {
            margin-left: 10px;
            font-style: italic;
        }
        button {
            padding: 10px 20px;
            background-color: orange;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover {
            background-color: #ff8c00;
        }
    </style>
</head>
<body>
    <div class="sidebar">
        <a href="/import">Import Data</a>
        <a href="#">Category</a>
        <a href="#">Charts</a>
        <a href="#">Export</a>
    </div>
    <div class="content">
        <h2>Import Data</h2>
        <form method="POST" enctype="multipart/form-data">
            <div class="file-input">
                <label for="file">Choose File</label>
                <input type="file" name="file" id="file" accept=".xls,.xlsx">
                <span class="file-name" id="file-name">{{ filename if filename else "No file chosen" }}</span>
            </div>
            <button type="submit">Import Data</button>
        </form>
        <script>
            const fileInput = document.getElementById('file');
            const fileNameSpan = document.getElementById('file-name');
            fileInput.addEventListener('change', () => {
                const file = fileInput.files[0];
                fileNameSpan.textContent = file ? file.name : "No file chosen";
            });
        </script>
    </div>
</body>
</html>
    ''', filename=filename)

if __name__ == "__main__":
    app.run(debug=True)
