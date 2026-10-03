from functools import wraps

from flask import g, jsonify, request

from core.jwtUtil import JwtUtils
from core.resp_model import respModel


def verify_request_token():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"message": "Token is missing"}), 401

    token = token.replace("Bearer ", "")
    payload = JwtUtils.verify_token(token)
    if not payload:
        return jsonify({"message": "Invalid token"}), 401

    g.user_payload = payload
    return None


def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        result = verify_request_token()
        if result:
            return result
        return f(*args, **kwargs)

    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        result = verify_request_token()
        if result:
            return result

        from sysmanage.model.user import User

        payload = getattr(g, "user_payload", {})
        user = User.query.filter_by(access_user_id=payload.get("access_user_id")).first()
        if not user or user.role != "admin":
            return respModel.error_resp("Only administrators can perform this operation")
        return f(*args, **kwargs)

    return decorated


def jwt_middleware():
    exclude_routes = [
        "/api/login",
        "/api/login/config",
        "/api/feishu/config",
        "/api/feishu/login",
        "/api/WebCollectionInfo/excuteTest",
        "/api/WebProject/queryAll",
        "/api/WebProject/query",
        "/api/WebCollectionInfo/queryByPage",
    ]
    exclude_prefixes = [
        "/api/ApiHistory/",
        "/api/WebHistory/",
        "/api/WebReportViewer/",
        "/api/WebCollectionInfo/excuteTest/",
    ]

    if request.path in exclude_routes:
        return None

    for prefix in exclude_prefixes:
        if request.path.startswith(prefix):
            return None

    return verify_request_token()
