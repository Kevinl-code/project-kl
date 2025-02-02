from flask import Flask, render_template, request, jsonify
import sqlite3
import pandas as pd
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# SQLite Database Configuration
DATABASE_PATH = "lazarus.db"

# Route to render the front page
@app.route('/')
def index():
    return render_template('index.html')

# Route to render the dashboard page
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# API endpoint to handle file upload and import data into SQLite
@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        # Get the uploaded file and table name from the request
        file = request.files['file']
        table_name = request.form['table_name']

        if not file or not table_name:
            return jsonify({"success": False, "message": "Please provide both file and table name."}), 400

        # Read the Excel file using pandas
        df = pd.read_excel(file)

  # Infer schema dynamically
        schema = {}
        check_constraints = {}

        for col in df.columns:
            # Determine the data type of the column
            dtype = str(df[col].dtype)
            if dtype.startswith("int"):
                schema[col] = "INT"
            elif dtype.startswith("float"):
                schema[col] = "REAL"
            else:
                schema[col] = "TEXT"

            # Check for potential CHECK constraints (categorical data)
            unique_values = df[col].dropna().unique()
            if len(unique_values) <= 10:  # Arbitrary threshold for categorical data
                check_constraints[col] = [str(val) for val in unique_values]

        # Connect to SQLite database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Create the table dynamically
        column_definitions = []
        for col, dtype in schema.items():
            if col in check_constraints:
                allowed_values = "', '".join(check_constraints[col])
                column_definition = f'"{col}" {dtype} CHECK("{col}" IN (\'{allowed_values}\'))'
            else:
                column_definition = f'"{col}" {dtype}'  # Escape column name with double quotes
            column_definitions.append(column_definition)

            create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_definitions)})"
            cursor.execute(create_table_sql)
        # Insert data into the table
        df.to_sql(table_name, conn, if_exists='append', index=False)

        # Commit and close the connection
        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": "Data imported successfully!"})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)