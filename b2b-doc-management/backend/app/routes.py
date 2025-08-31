from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Header
from fastapi.responses import JSONResponse, StreamingResponse
from app.services.auth_service import AuthService, SECRET_KEY
from app.services.file_upload import FileUploadService
from app.utils.db import SessionLocal
from app.models import Document, User
import json
import io
import pandas as pd
import jwt
import glob
import time

router = APIRouter(prefix="/api")


@router.post('/login')
def login(payload: dict):
    username = payload.get('username')
    password = payload.get('password')
    auth_service = AuthService()
    user = auth_service.login(username, password)
    if user:
        return JSONResponse({'message': 'Login successful', 'user': user}, status_code=200)
    raise HTTPException(status_code=401, detail='Invalid credentials')


@router.post('/upload')
def upload_file(file: UploadFile = File(...)):
    if not file or file.filename == '':
        raise HTTPException(status_code=400, detail='No selected file')
    file_upload_service = FileUploadService()
    # FastAPI UploadFile provides .file (a file-like object)
    result = file_upload_service.upload(file.file)
    return JSONResponse(result, status_code=201)


@router.post('/register')
def register(payload: dict):
    username = payload.get('username')
    password = payload.get('password')
    company = payload.get('company') or ''
    if not username or not password:
        raise HTTPException(status_code=400, detail='username and password required')
    from werkzeug.security import generate_password_hash
    db = SessionLocal()
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        db.close()
        raise HTTPException(status_code=400, detail='User exists')
    user = User(username=username, password=generate_password_hash(password), company_name=company)
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    import datetime
    payload = {'sub': user.id, 'username': user.username, 'company': user.company_name, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=8)}
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return JSONResponse({'message': 'User registered', 'token': token}, status_code=201)


def _get_bearer_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail='Unauthorized')
    return authorization.split(' ', 1)[1]


@router.get('/records')
def get_records(authorization: str = Depends(_get_bearer_token)):
    token = authorization
    try:
        jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except Exception:
        raise HTTPException(status_code=401, detail='Invalid token')
    all_records = []
    for path in glob.glob('/tmp/records_*.json'):
        with open(path, 'r', encoding='utf-8') as f:
            all_records.extend(json.load(f))
    return JSONResponse(all_records)


@router.get('/notifications')
def get_notifications():
    return JSONResponse({'notifications': []})


@router.delete('/record/{record_id}')
def delete_record(record_id: int, authorization: str = Depends(_get_bearer_token)):
    token = authorization
    try:
        jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except Exception:
        raise HTTPException(status_code=401, detail='Invalid token')
    removed = False
    for path in glob.glob('/tmp/records_*.json'):
        with open(path, 'r', encoding='utf-8') as f:
            arr = json.load(f)
        for i, r in enumerate(arr):
            if r.get('id') == record_id:
                arr.pop(i)
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(arr, f, ensure_ascii=False, indent=2)
                removed = True
                break
        if removed:
            break
    if removed:
        return JSONResponse({'message': 'Record deleted successfully'})
    raise HTTPException(status_code=404, detail='Record not found')


@router.post('/record/{record_id}/resubmit')
def resubmit_record(record_id: int, payload: dict):
    try:
        db = SessionLocal()
        doc = db.query(Document).filter(Document.id == record_id).first()
        if not doc:
            db.close()
            raise HTTPException(status_code=404, detail='Record not found')
        existing = []
        try:
            existing = json.loads(doc.resubmission) if doc.resubmission else []
        except Exception:
            existing = []
        existing.append({'payload': payload, 'ts': int(time.time() * 1000)})
        doc.resubmission = json.dumps(existing, ensure_ascii=False)
        doc.status = 'resubmitted'
        db.add(doc)
        db.commit()
        db.refresh(doc)
        db.close()
        return JSONResponse({'message': 'Record resubmitted'})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/records')
def create_record(payload: dict):
    required = ['company', 'type', 'speed', 'date', 'name']
    for r in required:
        if r not in payload:
            raise HTTPException(status_code=400, detail=f'Missing {r}')
    try:
        db = SessionLocal()
        user = db.query(User).filter(User.company_name == payload.get('company')).first()
        user_id = user.id if user else None
        doc = Document(user_id=user_id, document_type=payload.get('type'), urgency=payload.get('speed'), submission_date=payload.get('date'), customer_name=payload.get('name'), file_path=json.dumps(payload.get('files') or []), status='pending')
        db.add(doc)
        db.commit()
        db.refresh(doc)
        db.close()
        return JSONResponse({'message': 'Record created', 'id': doc.id}, status_code=201)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/export/{company}')
def export_company(company: str):
    try:
        db = SessionLocal()
        rows = db.query(Document).join(User, Document.user_id == User.id).filter(User.company_name == company).all()
        arr = []
        for r in rows:
            arr.append({
                'id': r.id,
                'customer_name': r.customer_name,
                'document_type': r.document_type,
                'urgency': r.urgency,
                'submission_date': r.submission_date.isoformat() if r.submission_date else None,
                'status': r.status,
                'file_path': r.file_path
            })
        df = pd.DataFrame(arr)
        output = io.BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)
        return StreamingResponse(io.BytesIO(output.read()), media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers={
            'Content-Disposition': f'attachment; filename="{company}_records.xlsx"'
        })
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail='No records for company')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
def register_routes(app):
    from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Header, Response
    from fastapi.responses import JSONResponse, StreamingResponse
    from app.services.auth_service import AuthService, SECRET_KEY
    from app.services.file_upload import FileUploadService
    from app.services.notification import NotificationService
    from app.utils.db import SessionLocal
    from app.models import Document, User
    import json
    import io
    import pandas as pd
    import jwt
    import glob
    import time
    
    router = APIRouter(prefix="/api")
    
    
    @router.post('/login')
    def login(payload: dict):
        username = payload.get('username')
        password = payload.get('password')
        auth_service = AuthService()
        user = auth_service.login(username, password)
        if user:
            return JSONResponse({'message': 'Login successful', 'user': user}, status_code=200)
        raise HTTPException(status_code=401, detail='Invalid credentials')
    
    
    @router.post('/upload')
    def upload_file(file: UploadFile = File(...)):
        if not file or file.filename == '':
            raise HTTPException(status_code=400, detail='No selected file')
        file_upload_service = FileUploadService()
        # FastAPI UploadFile is a SpooledTemporaryFile - pass file.file to save
        result = file_upload_service.upload(file.file)
        return JSONResponse(result, status_code=201)
    
    
    @router.post('/register')
    def register(payload: dict):
        username = payload.get('username')
        password = payload.get('password')
        company = payload.get('company') or ''
        if not username or not password:
            raise HTTPException(status_code=400, detail='username and password required')
        from werkzeug.security import generate_password_hash
        db = SessionLocal()
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            db.close()
            raise HTTPException(status_code=400, detail='User exists')
        user = User(username=username, password=generate_password_hash(password), company_name=company)
        db.add(user)
        db.commit()
        db.refresh(user)
        db.close()
        import datetime
        payload = {'sub': user.id, 'username': user.username, 'company': user.company_name, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=8)}
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return JSONResponse({'message': 'User registered', 'token': token}, status_code=201)
    
    
    def _get_bearer_token(authorization: str = Header(None)):
        if not authorization or not authorization.startswith('Bearer '):
            raise HTTPException(status_code=401, detail='Unauthorized')
        return authorization.split(' ', 1)[1]
    
    
    @router.get('/records')
    def get_records(authorization: str = Depends(_get_bearer_token)):
        token = authorization
        try:
            jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except Exception:
            raise HTTPException(status_code=401, detail='Invalid token')
        all_records = []
        for path in glob.glob('/tmp/records_*.json'):
            with open(path, 'r', encoding='utf-8') as f:
                all_records.extend(json.load(f))
        return JSONResponse(all_records)
    
    
    @router.get('/notifications')
    def get_notifications():
        return JSONResponse({'notifications': []})
    
    
    @router.delete('/record/{record_id}')
    def delete_record(record_id: int, authorization: str = Depends(_get_bearer_token)):
        token = authorization
        try:
            jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except Exception:
            raise HTTPException(status_code=401, detail='Invalid token')
        removed = False
        for path in glob.glob('/tmp/records_*.json'):
            with open(path, 'r', encoding='utf-8') as f:
                arr = json.load(f)
            for i, r in enumerate(arr):
                if r.get('id') == record_id:
                    arr.pop(i)
                    with open(path, 'w', encoding='utf-8') as f:
                        json.dump(arr, f, ensure_ascii=False, indent=2)
                    removed = True
                    break
            if removed:
                break
        if removed:
            return JSONResponse({'message': 'Record deleted successfully'})
        raise HTTPException(status_code=404, detail='Record not found')
    
    
    @router.post('/record/{record_id}/resubmit')
    def resubmit_record(record_id: int, payload: dict):
        try:
            db = SessionLocal()
            doc = db.query(Document).filter(Document.id == record_id).first()
            if not doc:
                db.close()
                raise HTTPException(status_code=404, detail='Record not found')
            existing = []
            try:
                existing = json.loads(doc.resubmission) if doc.resubmission else []
            except Exception:
                existing = []
            existing.append({'payload': payload, 'ts': int(time.time() * 1000)})
            doc.resubmission = json.dumps(existing, ensure_ascii=False)
            doc.status = 'resubmitted'
            db.add(doc)
            db.commit()
            db.refresh(doc)
            db.close()
            return JSONResponse({'message': 'Record resubmitted'})
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @router.post('/records')
    def create_record(payload: dict):
        required = ['company', 'type', 'speed', 'date', 'name']
        for r in required:
            if r not in payload:
                raise HTTPException(status_code=400, detail=f'Missing {r}')
        try:
            db = SessionLocal()
            user = db.query(User).filter(User.company_name == payload.get('company')).first()
            user_id = user.id if user else None
            doc = Document(user_id=user_id, document_type=payload.get('type'), urgency=payload.get('speed'), submission_date=payload.get('date'), customer_name=payload.get('name'), file_path=json.dumps(payload.get('files') or []), status='pending')
            db.add(doc)
            db.commit()
            db.refresh(doc)
            db.close()
            return JSONResponse({'message': 'Record created', 'id': doc.id}, status_code=201)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @router.get('/export/{company}')
    def export_company(company: str):
        try:
            db = SessionLocal()
            rows = db.query(Document).join(User, Document.user_id == User.id).filter(User.company_name == company).all()
            arr = []
            for r in rows:
                arr.append({
                    'id': r.id,
                    'customer_name': r.customer_name,
                    'document_type': r.document_type,
                    'urgency': r.urgency,
                    'submission_date': r.submission_date.isoformat() if r.submission_date else None,
                    'status': r.status,
                    'file_path': r.file_path
                })
            df = pd.DataFrame(arr)
            output = io.BytesIO()
            df.to_excel(output, index=False)
            output.seek(0)
            return StreamingResponse(io.BytesIO(output.read()), media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers={
                'Content-Disposition': f'attachment; filename="{company}_records.xlsx"'
            })
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail='No records for company')
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Header, Response
from fastapi.responses import JSONResponse, StreamingResponse
from app.services.auth_service import AuthService, SECRET_KEY
from app.services.file_upload import FileUploadService
from app.services.notification import NotificationService
from app.utils.db import SessionLocal
from app.models import Document, User
import json
import io
import pandas as pd
import jwt
import glob
import time

router = APIRouter(prefix="/api")


@router.post('/login')
def login(payload: dict):
    username = payload.get('username')
    password = payload.get('password')
    auth_service = AuthService()
    user = auth_service.login(username, password)
    if user:
        return JSONResponse({'message': 'Login successful', 'user': user}, status_code=200)
    raise HTTPException(status_code=401, detail='Invalid credentials')


@router.post('/upload')
def upload_file(file: UploadFile = File(...)):
    if not file or file.filename == '':
        raise HTTPException(status_code=400, detail='No selected file')
    file_upload_service = FileUploadService()
    # FastAPI UploadFile is a SpooledTemporaryFile - pass file.file to save
    result = file_upload_service.upload(file.file)
    return JSONResponse(result, status_code=201)


@router.post('/register')
def register(payload: dict):
    username = payload.get('username')
    password = payload.get('password')
    company = payload.get('company') or ''
    if not username or not password:
        raise HTTPException(status_code=400, detail='username and password required')
    from werkzeug.security import generate_password_hash
    db = SessionLocal()
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        db.close()
        raise HTTPException(status_code=400, detail='User exists')
    user = User(username=username, password=generate_password_hash(password), company_name=company)
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    import datetime
    payload = {'sub': user.id, 'username': user.username, 'company': user.company_name, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=8)}
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return JSONResponse({'message': 'User registered', 'token': token}, status_code=201)


def _get_bearer_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail='Unauthorized')
    return authorization.split(' ', 1)[1]


@router.get('/records')
def get_records(authorization: str = Depends(_get_bearer_token)):
    token = authorization
    try:
        jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except Exception:
        raise HTTPException(status_code=401, detail='Invalid token')
    all_records = []
    for path in glob.glob('/tmp/records_*.json'):
        with open(path, 'r', encoding='utf-8') as f:
            all_records.extend(json.load(f))
    return JSONResponse(all_records)


@router.get('/notifications')
def get_notifications():
    return JSONResponse({'notifications': []})


@router.delete('/record/{record_id}')
def delete_record(record_id: int, authorization: str = Depends(_get_bearer_token)):
    token = authorization
    try:
        jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except Exception:
        raise HTTPException(status_code=401, detail='Invalid token')
    removed = False
    for path in glob.glob('/tmp/records_*.json'):
        with open(path, 'r', encoding='utf-8') as f:
            arr = json.load(f)
        for i, r in enumerate(arr):
            if r.get('id') == record_id:
                arr.pop(i)
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(arr, f, ensure_ascii=False, indent=2)
                removed = True
                break
        if removed:
            break
    if removed:
        return JSONResponse({'message': 'Record deleted successfully'})
    raise HTTPException(status_code=404, detail='Record not found')


@router.post('/record/{record_id}/resubmit')
def resubmit_record(record_id: int, payload: dict):
    try:
        db = SessionLocal()
        doc = db.query(Document).filter(Document.id == record_id).first()
        if not doc:
            db.close()
            raise HTTPException(status_code=404, detail='Record not found')
        existing = []
        try:
            existing = json.loads(doc.resubmission) if doc.resubmission else []
        except Exception:
            existing = []
        existing.append({'payload': payload, 'ts': int(time.time() * 1000)})
        doc.resubmission = json.dumps(existing, ensure_ascii=False)
        doc.status = 'resubmitted'
        db.add(doc)
        db.commit()
        db.refresh(doc)
        db.close()
        return JSONResponse({'message': 'Record resubmitted'})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/records')
def create_record(payload: dict):
    required = ['company', 'type', 'speed', 'date', 'name']
    for r in required:
        if r not in payload:
            raise HTTPException(status_code=400, detail=f'Missing {r}')
    try:
        db = SessionLocal()
        user = db.query(User).filter(User.company_name == payload.get('company')).first()
        user_id = user.id if user else None
        doc = Document(user_id=user_id, document_type=payload.get('type'), urgency=payload.get('speed'), submission_date=payload.get('date'), customer_name=payload.get('name'), file_path=json.dumps(payload.get('files') or []), status='pending')
        db.add(doc)
        db.commit()
        db.refresh(doc)
        db.close()
        return JSONResponse({'message': 'Record created', 'id': doc.id}, status_code=201)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/export/{company}')
def export_company(company: str):
    try:
        db = SessionLocal()
        rows = db.query(Document).join(User, Document.user_id == User.id).filter(User.company_name == company).all()
        arr = []
        for r in rows:
            arr.append({
                'id': r.id,
                'customer_name': r.customer_name,
                'document_type': r.document_type,
                'urgency': r.urgency,
                'submission_date': r.submission_date.isoformat() if r.submission_date else None,
                'status': r.status,
                'file_path': r.file_path
            })
        df = pd.DataFrame(arr)
        output = io.BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)
        return StreamingResponse(io.BytesIO(output.read()), media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers={
            'Content-Disposition': f'attachment; filename="{company}_records.xlsx"'
        })
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail='No records for company')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))