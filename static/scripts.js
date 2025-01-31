let importedTableNames = [];

function navigateTo(page) {
    const content = document.getElementById('content');
    if (page === 'import') {
        content.innerHTML = 
            <h1>Import Data</h1>
            <form id="import-form">
                <label for="file_upload" style="font-size: larger;">Upload File (xlsx, excel):</label>
                <input type="file" id="file_upload" name="file_upload" accept=".xlsx,.xls" required>
                <br><br>
                <button type="button" id="import-button">Import Data</button>
                <br><br>
                <div id="table-name-placeholder" style="display: none;">
                    <label for="table_name" style="font-size: larger;">Enter Table Name:</label>
                    <input type="text" id="table_name" name="table_name" placeholder="Enter table name" required>
                    <br><br>
                    <button type="button" id="start-import-button">Start Import</button>
                </div>
            </form>
        ;
        attachImportEventHandlers();
    } else if (page === 'category') {
    content.innerHTML = 
        <h1>Category Management</h1>
        <form>
            <label for="table_dropdown" style="font-size: larger;">Select Table:</label>
            <select id="table_dropdown" style="padding-right: 50px;padding-bottom: 2px;padding-left: 50px;padding-top: 4px;">
                ${importedTableNames.map(table => <option value="${table}">${table}</option>).join('')}
            </select>
            <br><br>
            <label style="font-size: larger;">Select Year(s):</label>
            <div style="width: 800px;height: 119px;padding-top: 6px;padding-bottom: -;border-bottom-width: 8px;border-top-width: 9px;margin-bottom: 0px;">
                <input type="checkbox" id="all_years" name="year" value="all_years"> All Years<br>
                <input type="checkbox" class="year-option" name="year" value="2023" style="margin-top: 15px;margin-bottom: 5px;"> 2023<br>
                <input type="checkbox" class="year-option" name="year" value="2024" style="margin-top: 15px;margin-bottom: 5px;"> 2024<br>
                <input type="checkbox" class="year-option" name="year" value="2025" style="margin-top: 15px;"> 2025<br>
            </div>
            <br>
            <label for="chart_type" style="font-size: larger;">Select Chart Type:</label>
            <select id="chart_type" style="padding-right: 60px;padding-left: 60px;padding-bottom: 5px;padding-top: 5px;margin-left: 5px;">
                <option value="line">Line</option>
                <option value="bar">Bar</option>
                <option value="pie">Pie</option>
            </select>
            <br><br>
            <label for="x_axis" style="font-size: larger;margin-top: 10px;padding-top: 40px;">Select X Axis:</label>
            <select id="x_axis" style="padding-right: 60px;padding-left: 60px;padding-bottom: 5px;padding-top: 5px;margin-left: 5px;">
                <option value="op">op</option>
                <option value="mp">mp</option>
                <option value="lp">lp</option>
            </select>
            <br><br>
            <label for="y_axis" style="font-size: larger;">Select Y Axis:</label>
            <select id="y_axis" style="padding-right: 60px;padding-left: 60px;padding-top: 5px;padding-bottom: 5px;margin-left: 5px;">
                <option value="op">op</option>
                <option value="mp">mp</option>
                <option value="lp">lp</option>
            </select>
            <br><br>
            <label for="color_picker" style="font-size: larger;">Select Color:</label>
            <input type="color" id="color_picker" style="padding-right: 50px;padding-left: 40px;padding-top: 20px;margin-left: 5px;">
            <br><br>
            <input type="checkbox" id="grid_checkbox" style="width: 20px;height: 20px;margin-right: 5px;margin-top: 1px;margin-bottom: 1px;"> Show Grid
            <br><br>
            <button type="button" id="generate_chart_button">Generate Chart</button>
        </form>
    ;
    attachCategoryEventHandlers();

    } else if (page === 'chart') {
        content.innerHTML = 
            <h1>Chart Preview</h1>
            <img src="data:image/png;base64,{{ chart_image }}" alt="Chart Image">
            <br>
            <button onclick="navigateTo('export')">Export Chart</button>
        ;
    } else if (page === 'export') {
        content.innerHTML = 
            <h1>Export Chart</h1>
            <form action="/export" method="POST">
                <label for="export_type" style="font-size: larger;">Select Export Type:</label>
                <select name="export_type" id="export_type" required>
                    <option value="PDF">PDF</option>
                    <option value="ZIP">ZIP</option>
                    <option value="PNG">PNG</option>
                </select>
                <br><br>
                <label for="file_name" style="font-size: larger;">Enter File Name (without extension):</label>
                <input type="text" name="file_name" id="file_name" required>
                <br><br>
                <label for="file_location">Select Folder:</label>
                <input type="hidden" name="file_location" id="file_location">
                <button type="button" onclick="selectFolder()">Select Folder</button>
                <span id="selected-folder"></span>
                <br><br>
                <button type="submit">Save Export</button></form>
                ;
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
            // Save the table name to the dropdown list
            importedTableNames.push(tableName);
            alert("Data imported successfully.");
            navigateTo('category');
        }
    });
}

function attachCategoryEventHandlers() {
    const allYearsCheckbox = document.getElementById('all_years');
    const yearOptions = document.querySelectorAll('.year-option');
    const xAxisDropdown = document.getElementById('x_axis');
    const yAxisDropdown = document.getElementById('y_axis');
    const chartTypeDropdown = document.getElementById('chart_type');
    const generateChartButton = document.getElementById('generate_chart_button');

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

    xAxisDropdown.addEventListener('change', () => {
        const selectedValue = xAxisDropdown.value;
        Array.from(yAxisDropdown.options).forEach(option => {
            option.disabled = option.value === selectedValue;
        });
    });

    yAxisDropdown.addEventListener('change', () => {
        const selectedValue = yAxisDropdown.value;
        Array.from(xAxisDropdown.options).forEach(option => {
            option.disabled = option.value === selectedValue;
        });
    });

    generateChartButton.addEventListener('click', () => {
        const chartType = chartTypeDropdown.value;
        navigateTo('chart', { chartType });
    });
}

function selectFolder() {
    fetch('/select_folder', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.folder_path) {
                document.getElementById('file_location').value = data.folder_path;
                document.getElementById('selected-folder').innerText = data.folder_path;
            } else {
                const errorMessage = data.error || "No folder selected.";
                alert(errorMessage);
                document.getElementById('selected-folder').innerText = errorMessage;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert("An error occurred while selecting a folder.");
        });
}