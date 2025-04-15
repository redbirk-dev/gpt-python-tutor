from app import app, db, set_admin_user

def main():
    with app.app_context():
        # Create the is_admin column if it doesn't exist
        try:
            # This will fail if the column already exists
            db.session.execute('ALTER TABLE user ADD COLUMN is_admin BOOLEAN DEFAULT FALSE')
            db.session.commit()
            print("Added is_admin column to User table")
        except Exception as e:
            print(f"Column may already exist: {e}")
        
        # Set the admin user
        if set_admin_user('rudraat22@gmail.com'):
            print("Successfully set rudraat22@gmail.com as admin user")
        else:
            print("Failed to set admin user. Make sure the email exists in the database.")

if __name__ == "__main__":
    main() 