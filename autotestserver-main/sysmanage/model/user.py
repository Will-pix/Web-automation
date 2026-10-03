from extensions import database

# ORM
class User(database.Model):
    __tablename__ = "user"
    id = database.Column(database.Integer, primary_key=True, )
    username = database.Column(database.String(255), unique=True)
    password = database.Column(database.String(255))
    access_email = database.Column(database.String(255))
    access_name = database.Column(database.String(255))
    access_user_id = database.Column(database.String(255) , unique=True)
    role = database.Column(database.String(50), default="user")
    create_time = database.Column(database.DateTime)
