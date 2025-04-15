import os
from app import app, db
from models import User, Progress, QuizScore

def recreate_database():
    with app.app_context():
        # Drop all tables
        db.drop_all()
        print("Dropped all tables")
        
        # Create all tables with the new schema
        db.create_all()
        print("Created all tables with new schema")
        
        # Check if the admin user exists
        admin_user = User.query.filter_by(email='rudraat22@gmail.com').first()
        if not admin_user:
            print("Admin user not found. Please register with the email 'rudraat22@gmail.com' first.")
            return
        
        # Set the admin user
        admin_user.is_admin = True
        db.session.commit()
        print(f"Successfully set {admin_user.email} as admin user")

if __name__ == "__main__":
    recreate_database() 