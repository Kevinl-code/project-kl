from flask import Flask, request, jsonify, render_template
import sqlite3
import pandas as pd
import io

app = Flask(__name__)
DATABASE_FILE = "data_viz.db"

# Ensure SQLite database exists
def create_database():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.close()

# Function to import data into SQLite from an in-memory file
def import_data_to_sqlite(file_content, file_extension, table_name):
    try:
        conn = sqlite3.connect(DATABASE_FILE)

        if file_extension == ".csv":
            df = pd.read_csv(io.StringIO(file_content.decode('utf-8')))
        else:  # Assume Excel file
            df = pd.read_excel(io.BytesIO(file_content))

        # Insert data into dynamically created table
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        conn.close()
        return True, f"Data imported successfully into table '{table_name}'"
    except Exception as e:
        return False, str(e)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/import', methods=['POST'])
def import_data():
    create_database()  # Ensure database exists

    if 'file' not in request.files or 'tableName' not in request.form:
        return jsonify({"message": "File and table name are required!"}), 400

    file = request.files['file']
    table_name = request.form['tableName']

    if file.filename == '':
        return jsonify({"message": "No selected file!"}), 400

    file_content = file.read()  # Read file into memory
    file_extension = ".csv" if file.filename.endswith('.csv') else ".xlsx"

    success, message = import_data_to_sqlite(file_content, file_extension, table_name)
    
    return jsonify({"message": message}), (200 if success else 500)

if __name__ == '__main__':
    app.run(debug=True)
