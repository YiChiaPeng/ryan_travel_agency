from flask import Blueprint, request, jsonify
from app.services.auth import AuthService
from app.services.file_upload import FileUploadService
from app.utils.db import get_db_connection

bp = Blueprint('routes', __name__)

@bp.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    auth_service = AuthService()
    user = auth_service.login(username, password)
    if user:
        return jsonify({'message': 'Login successful', 'user': user}), 200
    return jsonify({'message': 'Invalid credentials'}), 401

@bp.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    file_upload_service = FileUploadService()
    result = file_upload_service.upload(file)
    return jsonify(result), 201

@bp.route('/api/records', methods=['GET'])
def get_records():
    db_connection = get_db_connection()
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM records")
    records = cursor.fetchall()
    return jsonify(records), 200

@bp.route('/api/notifications', methods=['GET'])
def get_notifications():
    # Logic to retrieve notifications for the user
    return jsonify({'notifications': []}), 200

@bp.route('/api/record/<int:record_id>', methods=['DELETE'])
def delete_record(record_id):
    db_connection = get_db_connection()
    cursor = db_connection.cursor()
    cursor.execute("DELETE FROM records WHERE id = %s", (record_id,))
    db_connection.commit()
    return jsonify({'message': 'Record deleted successfully'}), 200

@bp.route('/api/record/<int:record_id>/resubmit', methods=['POST'])
def resubmit_record(record_id):
    # Logic to handle resubmission of a record
    return jsonify({'message': 'Record resubmitted successfully'}), 200

# Register the blueprint in the main application
def register_routes(app):
    app.register_blueprint(bp)