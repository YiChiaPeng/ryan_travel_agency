
import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file_obj, upload_folder, filename=None):
    """Save either a Werkzeug file object or a file-like object to disk.
    file_obj can be one of:
      - Werkzeug FileStorage (has .filename and .save)
      - file-like with .read() (like FastAPI UploadFile.file)
    """
    actual_filename = None
    if filename:
        actual_filename = filename
    elif hasattr(file_obj, 'filename'):
        actual_filename = file_obj.filename

    if not actual_filename or not allowed_file(actual_filename):
        return None

    filename_safe = secure_filename(actual_filename)
    file_path = os.path.join(upload_folder, filename_safe)

    # If Werkzeug FileStorage with .save
    if hasattr(file_obj, 'save'):
        file_obj.save(file_path)
        return file_path

    # Otherwise assume file-like object; write in chunks
    try:
        with open(file_path, 'wb') as out_f:
            chunk = file_obj.read(4096)
            while chunk:
                out_f.write(chunk)
                chunk = file_obj.read(4096)
        return file_path
    except Exception:
        return None


class FileUploadService:
    def __init__(self, upload_folder: str = '/tmp/uploads'):
        self.upload_folder = upload_folder
        os.makedirs(self.upload_folder, exist_ok=True)

    def upload(self, file_obj, filename: str = None):
        """Save a file-like object or Werkzeug FileStorage to the configured folder.
        Returns dict with message and file_path or error.
        """
        path = save_file(file_obj, self.upload_folder, filename=filename)
        if path:
            return {'message': 'File uploaded successfully', 'file_path': path}
        return {'error': 'File type not allowed'}


# Explicit exports for safer imports from other modules
__all__ = [
    'allowed_file',
    'save_file',
    'upload_file',
    'FileUploadService'
]