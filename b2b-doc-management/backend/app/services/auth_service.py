import jwt
import datetime
from werkzeug.security import check_password_hash
from ..utils.db import SessionLocal
from ..models import User

SECRET_KEY = 'replace-with-secure-secret'


class AuthService:
    def __init__(self):
        self.db = SessionLocal()

    def login(self, username, password):
        user = self.db.query(User).filter(User.username == username).first()
        if not user:
            return None

        if check_password_hash(user.password, password):
            payload = {
                'sub': user.id,
                'username': user.username,
                'company': user.company_name,
                'is_admin': int(getattr(user, 'is_admin', 0)),
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=8)
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
            return {'id': user.id, 'username': user.username, 'company': user.company_name, 'token': token}

        return None
