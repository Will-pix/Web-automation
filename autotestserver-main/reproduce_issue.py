from app import application
from extensions import database
from webtest.model.WebProjectModel import WebProject

def test_insert():
    with application.app_context():
        print("db instance in app:", database)
        print("db instance in model:", WebProject.query.session)
        
        project = WebProject(project_name="Test Project", project_desc="Test Desc")
        database.session.add(project)
        try:
            database.session.commit()
            print("Successfully added project")
        except Exception as e:
            print("Error adding project:", e)
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_insert()
