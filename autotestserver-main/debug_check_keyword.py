from app import application
from webtest.model.WebKeyWordModel import WebKeyWord
from extensions import database

with application.app_context():
    keyword_name = "AI融合视觉"
    keyword = WebKeyWord.query.filter(WebKeyWord.name.like(f"%{keyword_name}%")).first()
    if keyword:
        print(f"Found keyword: {keyword.name}, ID: {keyword.id}, OperationTypeID: {keyword.operation_type_id}")
    else:
        print(f"Keyword '{keyword_name}' not found.")
