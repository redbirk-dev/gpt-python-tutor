from app import app, db
from models import User

def make_admin():
    with app.app_context():
        # Find the user by email
        user = User.query.filter_by(email='rudraat22@gmail.com').first()
        
        if user:
            # Set the user as admin
            user.is_admin = True
            db.session.commit()
            print(f"Successfully set {user.email} as admin user")
        else:
            print("User not found. Make sure the email exists in the database.")

if __name__ == "__main__":
    make_admin() 