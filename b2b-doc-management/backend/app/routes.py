from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse
from app.services.file_upload import FileUploadService
from app.utils.db import SessionLocal
from app.models import Document, User
from app.middleware.auth import get_current_user, verify_user_permission, verify_company_permission
import json
import io
import pandas as pd
import glob
import time

router = APIRouter(prefix="/api")


@router.post('/upload')
def upload_file(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    """文件上傳端點"""
    if not file or file.filename == '':
        raise HTTPException(status_code=400, detail='No selected file')
    
    file_upload_service = FileUploadService()
    result = file_upload_service.upload(file.file)
    return JSONResponse(result, status_code=201)


@router.get('/records')
def get_records(current_user: User = Depends(get_current_user)):
    """獲取記錄列表"""
    all_records = []
    for path in glob.glob('/tmp/records_*.json'):
        with open(path, 'r', encoding='utf-8') as f:
            all_records.extend(json.load(f))
    return JSONResponse(all_records)


@router.get('/notifications')
def get_notifications(current_user: User = Depends(get_current_user)):
    """獲取通知列表"""
    return JSONResponse({'notifications': []})


@router.delete('/record/{record_id}')
def delete_record(record_id: int, current_user: User = Depends(get_current_user)):
    """刪除記錄"""
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
def resubmit_record(record_id: int, payload: dict, current_user: User = Depends(get_current_user)):
    """重新提交記錄"""
    try:
        db = SessionLocal()
        doc = db.query(Document).filter(Document.id == record_id).first()
        if not doc:
            db.close()
            raise HTTPException(status_code=404, detail='Record not found')
        
        # 檢查用戶權限（只能操作自己的記錄或管理員）
        if not verify_user_permission(current_user, doc.user_id):
            db.close()
            raise HTTPException(status_code=403, detail='Permission denied')
        
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
def create_record(payload: dict, current_user: User = Depends(get_current_user)):
    """創建新記錄"""
    required = ['type', 'speed', 'date', 'name']
    for r in required:
        if r not in payload:
            raise HTTPException(status_code=400, detail=f'Missing {r}')
    
    try:
        db = SessionLocal()
        # 使用當前用戶的信息
        doc = Document(
            user_id=current_user.id,
            document_type=payload.get('type'),
            urgency=payload.get('speed'),
            submission_date=payload.get('date'),
            customer_name=payload.get('name'),
            file_path=json.dumps(payload.get('files') or []),
            status='pending'
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        db.close()
        return JSONResponse({'message': 'Record created', 'id': doc.id}, status_code=201)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/export/{company}')
def export_company(company: str, current_user: User = Depends(get_current_user)):
    """導出公司記錄"""
    # 檢查權限：只能導出自己公司的數據或管理員
    if not verify_company_permission(current_user, company):
        raise HTTPException(status_code=403, detail='Permission denied')
    
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
        return StreamingResponse(
            io.BytesIO(output.read()),
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={'Content-Disposition': f'attachment; filename="{company}_records.xlsx"'}
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail='No records for company')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
