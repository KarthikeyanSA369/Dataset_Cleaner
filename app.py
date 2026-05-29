# app.py
import os
import pandas as pd
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename

# --- Data Cleaning Logic ---
def clean_csv_data(input_file_path):
    df = pd.read_csv(input_file_path)
    df.dropna(inplace=True)
    df.drop_duplicates(inplace=True)
    return df

# --- Flask Setup ---
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create uploads folder if not exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Allowed file check
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'csvFile' not in request.files:
        return jsonify({"status": "error", "message": "No file uploaded"}), 400
    
    file = request.files['csvFile']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No file selected"}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            cleaned_df = clean_csv_data(filepath)
            cleaned_filename = "cleaned_" + filename
            cleaned_filepath = os.path.join(app.config['UPLOAD_FOLDER'], cleaned_filename)
            cleaned_df.to_csv(cleaned_filepath, index=False)

            return jsonify({
                "status": "success",
                "message": "File cleaned successfully!",
                "cleaned_file": cleaned_filename,
                "rows_removed_na": len(pd.read_csv(filepath)) - len(cleaned_df),
                "rows_removed_duplicates": len(pd.read_csv(filepath).drop_duplicates()) - len(cleaned_df)
            })
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    else:
        return jsonify({"status": "error", "message": "Invalid file type. Only CSV allowed"}), 400

# Route to download cleaned files
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
