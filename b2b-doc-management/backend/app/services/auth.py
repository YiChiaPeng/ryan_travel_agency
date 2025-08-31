from fastapi import APIRouter, HTTPException
from werkzeug.security import generate_password_hash, check_password_hash
from ..utils.db import get_db_connection

router = APIRouter(prefix="/auth")


@router.post('/login')
def login(payload: dict):
    username = payload.get('username')
    password = payload.get('password')

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

    if user and check_password_hash(user['password'], password):
        return {'message': 'Login successful'}
    raise HTTPException(status_code=401, detail='Invalid username or password')


@router.post('/register')
def register(payload: dict):
    username = payload.get('username')
    password = payload.get('password')

    hashed_password = generate_password_hash(password)

    conn = get_db_connection()
    conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
    conn.commit()

    return {'message': 'User registered successfully'}


@router.post('/logout')
def logout():
    return {'message': 'Logout successful'}