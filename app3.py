import matplotlib
matplotlib.use('Agg')  # Use Agg backend for non-GUI support

from flask import Flask, render_template, request, jsonify
import os
import matplotlib.pyplot as plt
import zipfile
import io
import base64
import subprocess
import json

app = Flask(__name__)

# Store chart figure in memory
fig = None
chart_type = "line"  # Default chart type


@app.route('/')
def chart():
    global fig, chart_type
    # Example chart data
    data = {
        'data1': [1, 2, 3, 4],
        'data2': [10, 20, 30, 40]
    }

    # Generate chart based on selected type
    fig, ax = plt.subplots()
    if chart_type == "line":
        ax.plot(data['data1'], label='Data 1')
        ax.plot(data['data2'], label='Data 2')
    elif chart_type == "bar":
        x = range(len(data['data1']))
        ax.bar(x, data['data1'], label='Data 1', alpha=0.7)
        ax.bar(x, data['data2'], label='Data 2', alpha=0.7)
    elif chart_type == "pie":
        ax.pie(data['data1'], labels=['A', 'B', 'C', 'D'], autopct='%1.1f%%')

    ax.set_title(f"{chart_type.capitalize()} Chart")
    if chart_type != "pie":
        ax.legend()

    # Save chart temporarily in memory
    img_stream = io.BytesIO()
    fig.savefig(img_stream, format='png')
    img_stream.seek(0)

    # Encode image as base64 string
    chart_image_base64 = base64.b64encode(img_stream.getvalue()).decode('utf-8')
    return render_template('index3.html', chart_image=chart_image_base64, page="chart")


@app.route('/category', methods=['POST'])
def set_chart_type():
    global chart_type
    chart_type = request.form.get("chart_type", "line")
    return jsonify({"status": "success", "chart_type": chart_type})


@app.route('/export', methods=['GET', 'POST'])
def export_chart():
    global fig
    message = None

    if request.method == 'POST':
        if fig is None:
            message = "No chart found. Please generate a chart first."
        else:
            export_type = request.form['export_type']
            file_name = request.form['file_name']
            file_location = request.form['file_location']

            # Validate directory path
            if not os.path.isdir(file_location):
                message = "Invalid directory. Please select or enter a valid directory."
            else:
                try:
                    if export_type == "PDF":
                        pdf_path = os.path.join(file_location, f"{file_name}.pdf")
                        fig.savefig(pdf_path, format="pdf")
                        message = f"Chart saved as PDF at {pdf_path}"

                    elif export_type == "ZIP":
                        zip_path = os.path.join(file_location, f"{file_name}.zip")
                        image_path = os.path.join(file_location, f"{file_name}.png")

                        fig.savefig(image_path, format="png")

                        with zipfile.ZipFile(zip_path, 'w') as zipf:
                            zipf.write(image_path, os.path.basename(image_path))
                        os.remove(image_path)

                        message = f"Chart saved as ZIP at {zip_path}"

                    elif export_type == "Image":
                        image_path = os.path.join(file_location, f"{file_name}.png")
                        fig.savefig(image_path, format="png")
                        message = f"Chart saved as Image at {image_path}"
                except Exception as e:
                    message = f"Error saving file: {str(e)}"

    return render_template('index3.html', page="export", message=message)


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
