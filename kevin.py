from flask import Flask, render_template_string, request, jsonify
import os
import matplotlib.pyplot as plt
import zipfile
import io
import base64
import subprocess

app = Flask(__name__)

# Store chart figure in memory
fig = None

# Template for the entire application
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chart Export</title>
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
            padding: 0;
            display: flex;
            flex-direction: column;
            gap: 1cm;
            font-family: Arial, sans-serif;
        }
        .sidebar a {
            color: white;
            text-decoration: none;
            margin: 10px 0;
            padding: 10px;
            border-radius: 5px;
            font-size: 1.6rem;
            cursor: pointer;
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
        .message {
            margin-top: 20px;
            padding: 10px;
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
            border-radius: 5px;
            font-family: Arial, sans-serif;
        }
        h1, h2 {
            font-family: Arial, sans-serif;
        }
        input, select {
            padding: 10px;
            font-size: 1rem;
            margin-top: 5px;
        }
    </style>
    <script>
        let importedTableNames = [];

        function navigateTo(page) {
            const content = document.getElementById('content');
            if (page === 'import') {
                content.innerHTML = `
                    <h1>Import Data</h1>
                    <form id="import-form">
                        <label for="file_upload">Upload File (xlsx, excel):</label>
                        <input type="file" id="file_upload" name="file_upload" accept=".xlsx,.xls" required>
                        <br><br>
                        <button type="button" id="import-button">Import Data</button>
                        <br><br>
                        <div id="table-name-placeholder" style="display: none;">
                            <label for="table_name">Enter Table Name:</label>
                            <input type="text" id="table_name" name="table_name" placeholder="Enter table name" required>
                            <br><br>
                            <button type="button" id="start-import-button">Start Import</button>
                        </div>
                    </form>
                `;
                attachImportEventHandlers();
            } else if (page === 'category') {
                content.innerHTML = `
                    <h1>Category Management</h1>
                    <form>
                        <label for="table_dropdown">Select Table:</label>
                        <select id="table_dropdown">
                            ${importedTableNames.map(table => `<option value="${table}">${table}</option>`).join('')}
                        </select>
                        <br><br>
                        <label>Select Year(s):</label>
                        <div>
                            <input type="checkbox" id="all_years" name="year" value="all_years"> All Years<br>
                            <input type="checkbox" class="year-option" name="year" value="2023"> 2023<br>
                            <input type="checkbox" class="year-option" name="year" value="2024"> 2024<br>
                            <input type="checkbox" class="year-option" name="year" value="2025"> 2025<br>
                        </div>
                        <br>
                        <label for="chart_type">Select Chart Type:</label>
                        <select id="chart_type">
                            <option value="line">Line</option>
                            <option value="bar">Bar</option>
                            <option value="pie">Pie</option>
                        </select>
                        <br><br>
                        <button type="button" id="generate_chart_button">Generate Chart</button>
                    </form>
                `;
                attachCategoryEventHandlers();
            } else if (page === 'chart') {
                fetch('/chart').then(response => response.text()).then(html => {
                    content.innerHTML = html;
                });
            } else if (page === 'export') {
                fetch('/export').then(response => response.text()).then(html => {
                    content.innerHTML = html;
                });
            }
        }

        function attachImportEventHandlers() {
            const importButton = document.getElementById('import-button');
            const startImportButton = document.getElementById('start-import-button');
            const tableNamePlaceholder = document.getElementById('table-name-placeholder');

            importButton.addEventListener('click', () => {
                const fileUpload = document.getElementById('file_upload');
                if (fileUpload.files.length === 0) {
                    alert("Please upload a file before proceeding.");
                } else {
                    tableNamePlaceholder.style.display = 'block';
                }
            });

            startImportButton.addEventListener('click', () => {
                const tableName = document.getElementById('table_name').value.trim();
                if (!tableName) {
                    alert("Please enter a table name.");
                } else {
                    importedTableNames.push(tableName);
                    alert("Data imported successfully.");
                    navigateTo('category');
                }
            });
        }

        function attachCategoryEventHandlers() {
            const allYearsCheckbox = document.getElementById('all_years');
            const yearOptions = document.querySelectorAll('.year-option');

            allYearsCheckbox.addEventListener('change', () => {
                if (allYearsCheckbox.checked) {
                    yearOptions.forEach(option => option.disabled = true);
                } else {
                    yearOptions.forEach(option => option.disabled = false);
                }
            });

            yearOptions.forEach(option => {
                option.addEventListener('change', () => {
                    if (Array.from(yearOptions).some(opt => opt.checked)) {
                        allYearsCheckbox.checked = false;
                    }
                });
            });
        }
    </script>
</head>
<body>
    <div class="sidebar">
        <a onclick="navigateTo('import')">Import Data</a>
        <a onclick="navigateTo('category')">Category</a>
        <a onclick="navigateTo('chart')">Chart</a>
        <a onclick="navigateTo('export')">Export</a>
    </div>
    <div class="content" id="content">
        <h1>Welcome</h1>
        <p>Select an option from the sidebar to get started.</p>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(html_template)

@app.route('/chart', methods=['GET'])
def chart():
    global fig
    chart_type = request.args.get('chart_type', 'line')

    data = {
        'data1': [1, 2, 3, 4],
        'data2': [10, 20, 30, 40]
    }

    fig, ax = plt.subplots()
    if chart_type == 'line':
        ax.plot(data['data1'], label='Data 1')
        ax.plot(data['data2'], label='Data 2')
    elif chart_type == 'bar':
        ax.bar(range(len(data['data1'])), data['data1'], label='Data 1')
        ax.bar(range(len(data['data2'])), data['data2'], label='Data 2')
    elif chart_type == 'pie':
        ax.pie(data['data1'], labels=['A', 'B', 'C', 'D'], autopct='%1.1f%%')

    ax.legend()

    img_stream = io.BytesIO()
    fig.savefig(img_stream, format='png')
    img_stream.seek(0)
    chart_image_base64 = base64.b64encode(img_stream.getvalue()).decode('utf-8')

    return f"<h1>Chart Preview</h1><img src='data:image/png;base64,{chart_image_base64}'><br><button onclick=\"navigateTo('export')\">Export Chart</button>"

@app.route('/export', methods=['GET', 'POST'])
def export_chart():
    return "<h1>Export Page</h1>"  # Placeholder export page

if __name__ == '__main__':
    app.run(debug=True)
