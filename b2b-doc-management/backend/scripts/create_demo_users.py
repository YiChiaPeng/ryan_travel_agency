from app.utils.db import init_db, SessionLocal
from app.models import User
from werkzeug.security import generate_password_hash


def create_demo():
    init_db()
    db = SessionLocal()
    # create admin
    admin = db.query(User).filter(User.username=='admin').first()
    if not admin:
        admin_user = User(username='admin', password=generate_password_hash('adminpass'), company_name='Internal', is_admin=1)
        db.add(admin_user)
    # create a sample B2B user
    b2b = db.query(User).filter(User.username=='b2b_company').first()
    if not b2b:
        b2b_user = User(username='b2b_company', password=generate_password_hash('password'), company_name='Acme Travel', is_admin=0)
        db.add(b2b_user)
    db.commit()
    db.close()
    print('Demo users created: admin/adminpass, b2b_company/password')

if __name__ == '__main__':
    create_demo()
