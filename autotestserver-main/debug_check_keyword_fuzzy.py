from app import application
from webtest.model.WebKeyWordModel import WebKeyWord
from extensions import database

with application.app_context():
    keywords = WebKeyWord.query.filter((WebKeyWord.name.like("%AI%")) | (WebKeyWord.name.like("%视觉%"))).all()
    if keywords:
        for k in keywords:
            print(f"Found: {k.name}, ID: {k.id}")
    else:
        print("No AI/Vision keywords found.")
