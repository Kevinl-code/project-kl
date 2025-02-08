from flask import Flask, render_template, request, jsonify
import sqlite3
import pandas as pd
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# SQLite Database Configuration
DATABASE_PATH = "lazarus.db"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        file = request.files['file']
        table_name = request.form['table_name']

        if not file or not table_name:
            return jsonify({"success": False, "message": "Please provide both file and table name."}), 400

        df = pd.read_excel(file)
        schema = {}
        check_constraints = {}

        for col in df.columns:
            dtype = str(df[col].dtype)
            if dtype.startswith("int"):
                schema[col] = "INT"
            elif dtype.startswith("float"):
                schema[col] = "REAL"
            else:
                schema[col] = "TEXT"

            unique_values = df[col].dropna().unique()
            if len(unique_values) <= 10:
                check_constraints[col] = [str(val) for val in unique_values]

        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        column_definitions = []
        for col, dtype in schema.items():
            if col in check_constraints:
                allowed_values = "', '".join(val.replace("'", "''") for val in check_constraints[col])
                column_definition = f'"{col}" {dtype} CHECK("{col}" IN (\'{allowed_values}\'))'
            else:
                column_definition = f'"{col}" {dtype}'
            column_definitions.append(column_definition)

        create_table_sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({", ".join(column_definitions)})'
        cursor.execute(create_table_sql)

        df.to_sql(table_name, conn, if_exists='append', index=False)

        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": "Data imported successfully!"})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/get_tables', methods=['GET'])
def get_tables():
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        return jsonify({"success": True, "tables": tables})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/get_columns', methods=['POST'])
def get_columns():
    try:
        table_name = request.json.get('table_name')
        if not table_name:
            return jsonify({"success": False, "message": "Table name is required."}), 400

        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        table_check = cursor.fetchone()

        if not table_check:
            print(f"DEBUG: Table '{table_name}' does not exist.")
            return jsonify({"success": False, "message": "Table does not exist."}), 404

        # Fetch column names
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]

        print(f"DEBUG: Retrieved columns: {columns}")  # Debugging output

        conn.close()

        if not columns:
            print(f"DEBUG: No columns found in table '{table_name}'")
            return jsonify({"success": False, "message": "No columns found in the table."}), 404

        return jsonify({"success": True, "columns": columns})

    except Exception as e:
        print(f"ERROR: {e}")  # Debugging output
        return jsonify({"success": False, "message": f"Error fetching columns: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
