# app/routes.py
import os
import uuid
from flask import Blueprint, request, jsonify, send_file, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from app.pdf_processing import extract_text_and_images
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

main = Blueprint('main', __name__)

# Ensure the temporary folder exists within the project
TEMP_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp')
if not os.path.exists(TEMP_FOLDER):
    os.makedirs(TEMP_FOLDER)

# Temporary storage for processed files (in-memory or database in production)
processed_files = {}

@main.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@main.route('/upload', methods=['POST']) # type: ignore
def upload():
    try:
        if 'file' not in request.files:
            return render_template('index.html', error="No file part in the request"), 400
        
        file = request.files['file']
        if file.filename == '':
            return render_template('index.html', error="No file selected for uploading"), 400
        
        if file:
            filename = secure_filename(file.filename) # type: ignore
            temp_path = os.path.join(TEMP_FOLDER, filename)
            file.save(temp_path)

            # Process the PDF
            extracted_text = extract_text_and_images(temp_path)

            if not extracted_text:
                return render_template('index.html', error="Failed to extract text from the PDF"), 500
            
            # Save processed text temporarily in the temp folder within the project
            job_id = str(uuid.uuid4())
            text_filename = f"{job_id}.txt"
            text_file_path = os.path.join(TEMP_FOLDER, text_filename)
            with open(text_file_path, 'w', encoding='utf-8') as text_file:
                text_file.write(extracted_text)
            
            # Store file reference with job ID
            processed_files[job_id] = text_file_path
            logger.info(f"Stored file for job ID {job_id}: {text_file_path}")

            # Redirect to the preview page with the job ID
            return redirect(url_for('main.preview', job_id=job_id))
    
    except Exception as e:
        logger.error(f"Error during file upload and processing: {e}")
        return render_template('index.html', error="An error occurred while processing the file"), 500

@main.route('/status/<job_id>', methods=['GET'])
def status(job_id):
    logger.info(f"Checking status for job ID {job_id}")
    if job_id in processed_files:
        logger.info(f"Job ID {job_id} found with file: {processed_files[job_id]}")
        return jsonify({"status": "completed", "file_id": job_id}), 200
    else:
        logger.warning(f"Job ID {job_id} not found")
        return jsonify({"status": "not found"}), 404

@main.route('/download/<file_id>', methods=['GET'])
def download(file_id):
    try:
        logger.info(f"Attempting to download file for job ID {file_id}")
        if file_id not in processed_files:
            logger.warning(f"File ID {file_id} not found in processed files")
            return jsonify({"error": "File not found"}), 404

        file_path = processed_files[file_id]
        return send_file(file_path, as_attachment=True)
    
    except Exception as e:
        logger.error(f"Error during file download: {e}")
        return jsonify({"error": "An error occurred while processing the download request"}), 500
        
@main.route('/preview/<job_id>', methods=['GET'])
def preview(job_id):
    """
    Route to preview the extracted text, highlight sections, and provide options for download and re-do.
    """
    try:
        if job_id not in processed_files:
            return jsonify({"error": "File not found"}), 404

        file_path = processed_files[job_id]
        
        # Read the extracted text
        with open(file_path, 'r', encoding='utf-8') as text_file:
            extracted_text = text_file.read()

        # Generate the download URL using the correct blueprint name
        download_url = url_for('main.download', file_id=job_id)

        # Render the preview template
        return render_template('preview.html', job_id=job_id, extracted_text=extracted_text, download_url=download_url)
    
    except Exception as e:
        logger.error(f"Error during preview rendering: {e}")
        return jsonify({"error": "An error occurred while processing the preview request"}), 500