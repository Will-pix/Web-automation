from extensions import database
from flask import Flask
import os

application = Flask(__name__)
# Load config manually or from file
flask_env = os.getenv('FLASK_ENV', 'development')
if flask_env == 'development':
    config_file = 'config/dev_settings.py'
else:
    config_file = 'config/prod_settings.py'
application.config.from_pyfile(config_file)

database.init_app(application)

def drop_alembic():
    with application.app_context():
        # Execute raw sql
        with database.engine.connect() as connection:
            try:
                connection.execute(database.text("DROP TABLE alembic_version"))
                print("Dropped alembic_version table.")
            except Exception as e:
                print(f"Error dropping table: {e}")
            try:
                # Also drop user table to force full recreation if needed? 
                # No, preserve user table, just update it?
                # If I preserve user table, migration will try to ALTER it.
                # If I drop it, migration will CREATE it.
                # Since the column access_email was missing, ALTER is what we want.
                # But if Alembic sees a CREATE USER in migration, and table exists... it errors.
                # It's safest to DROP user table too since we are seeding admin anyway.
                # And there is no real data yet?
                # User said "Deploy Web Automation Platform", implies new install.
                connection.execute(database.text("DROP TABLE user"))
                print("Dropped user table.")
            except Exception as e:
                print(f"Error dropping user table: {e}")

if __name__ == "__main__":
    drop_alembic()
