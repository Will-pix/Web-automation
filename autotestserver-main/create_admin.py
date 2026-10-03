from app import application
from extensions import database
from sysmanage.model.user import User

def create_admin():
    with application.app_context():
        # Check if admin exists
        if not User.query.filter_by(username='admin').first():
            user = User(
                username='admin',
                password='123456', # Plaintext as per controller
                access_name='Administrator',
                access_user_id='001',
                access_email='admin@example.com',
                role='admin'
            )
            database.session.add(user)
            database.session.commit()
            print("Admin user created.")
        else:
            print("Admin user already exists.")

if __name__ == "__main__":
    create_admin()
