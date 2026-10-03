import sys
import os

# Add parent directory to path so we can import app and extensions
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import application
from extensions import database
from sqlalchemy import text
from sysmanage.model.user import User

def upgrade_database():
    with application.app_context():
        engine = database.engine
        
        # Check if column already exists
        # This works for both MySQL and SQLite
        try:
            with engine.connect() as conn:
                try:
                    # Try to select the role column. If it fails, it doesn't exist.
                    conn.execute(text("SELECT role FROM user LIMIT 1"))
                    print("Column 'role' already exists in the 'user' table.")
                    column_exists = True
                except Exception as e:
                    column_exists = False

                if not column_exists:
                    print("Adding 'role' column to 'user' table...")
                    # Add role column
                    conn.execute(text("ALTER TABLE user ADD COLUMN role VARCHAR(50) DEFAULT 'user'"))
                    conn.commit()
                    print("Column 'role' added successfully.")
                
                # Make existing admin a real admin
                print("Setting 'admin' user role to 'admin'...")
                conn.execute(text("UPDATE user SET role = 'admin' WHERE username = 'admin'"))
                conn.commit()
                print("Upgrade completed successfully.")
                
        except Exception as e:
            print(f"Error upgrading database: {e}")

if __name__ == "__main__":
    upgrade_database()
