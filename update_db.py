from app import app, db
from models import User, Progress, QuizScore, Visitor

def update_database():
    with app.app_context():
        # Create all tables that don't exist yet
        db.create_all()
        print("Database schema updated successfully!")

if __name__ == "__main__":
    update_database() 