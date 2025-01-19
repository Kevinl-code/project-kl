from flask import Flask, render_template, request, jsonify, session
import matplotlib.pyplot as plt
import io
import base64
import os
import zipfile
import subprocess
import shutil


app = Flask(__name__)  # Define the Flask app object
app.secret_key = 'your_secret_key'  # Needed for using session

@app.route('/chart', methods=['GET'])
def chart():
    chart_type = request.args.get('chart_type', 'line')  # Default to 'line'

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
        ax.pie(data['data1'], labels=['Data 1'], autopct='%1.1f%%')
        ax.pie(data['data2'], labels=['Data 2'], autopct='%1.1f%%')

    ax.set_title(f"Example {chart_type.capitalize()} Chart")
    ax.legend()

    # Save chart as a temporary image
    img_stream = io.BytesIO()
    fig.savefig(img_stream, format='png')
    img_stream.seek(0)

    # Save the image temporarily
    temp_img_path = 'static/temp_chart.png'
    with open(temp_img_path, 'wb') as f:
        f.write(img_stream.read())

    # Store the image path in session
    session['chart_image_path'] = temp_img_path

    # Convert to base64 for display
    chart_image_base64 = base64.b64encode(img_stream.getvalue()).decode('utf-8')

    return render_template('index2.html', chart_image=chart_image_base64, page="chart")

@app.route('/export', methods=['GET', 'POST'])
def export_chart():
    # Retrieve chart image path from session
    chart_image_path = session.get('chart_image_path', None)
    if not chart_image_path:
        return jsonify({'message': "No chart found. Please generate a chart first.", 'file_path': None})

    message = None
    file_path = None

    if request.method == 'POST':
        export_type = request.form['export_type']
        file_name = request.form['file_name']
        file_location = request.form['file_location']

        # Check if the selected folder is valid
        if not os.path.isdir(file_location):
            message = "Invalid directory. Please select or enter a valid directory."
        else:
            try:
                sanitized_file_name = file_name.replace(" ", "_").replace("/", "_").replace("\\", "_")

                # Export PNG
                if export_type == "PNG":
                    file_path = os.path.join(file_location, f"{sanitized_file_name}.png")
                    shutil.copy(chart_image_path, file_path)  # Copy the temp chart to the selected folder
                    message = f"Chart saved as Image at {file_path}"

                # Export PDF
                elif export_type == "PDF":
                    file_path = os.path.join(file_location, f"{sanitized_file_name}.pdf")
                    fig.savefig(file_path, format="pdf")
                    message = f"Chart saved as PDF at {file_path}"

                # Export ZIP
                elif export_type == "ZIP":
                    zip_path = os.path.join(file_location, f"{sanitized_file_name}.zip")
                    with zipfile.ZipFile(zip_path, 'w') as zipf:
                        zipf.write(chart_image_path, os.path.basename(chart_image_path))  # Add the image to the ZIP
                    file_path = zip_path
                    message = f"Chart saved as ZIP at {file_path}"

            except Exception as e:
                message = f"Error saving file: {str(e)}"

    return jsonify({'message': message, 'file_path': file_path})


@app.route('/select_folder', methods=['POST'])
def select_folder():
    """Use subprocess to open a folder selection dialog and return the path."""
    try:
        # Call a Python script to use tkinter in a subprocess
        result = subprocess.run(
            ['python', 'select_folder_helper.py'],  # Use 'python' if 'python3' is unavailable
            capture_output=True,
            text=True
        )

        # Log subprocess output
        print("Subprocess Output:", result.stdout)
        print("Subprocess Error:", result.stderr)

        folder_path = result.stdout.strip()

        if folder_path and folder_path != "No folder selected.":
            return jsonify({'folder_path': folder_path})
        else:
            error_message = result.stderr.strip() or "No folder selected."
            return jsonify({'folder_path': None, 'error': error_message})
    except Exception as e:
        return jsonify({'folder_path': None, 'error': str(e)})
if __name__ == '__main__':
    app.run(debug=True)
