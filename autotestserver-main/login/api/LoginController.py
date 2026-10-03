from flask import Blueprint, request

from core.jwtUtil import JwtUtils
from core.resp_model import respModel
from platformconfig.service.runtime_store import load_settings
from sysmanage.model.user import User

module_route = Blueprint("route_login", __name__)


@module_route.route("/login", methods=["POST"])
def login():
    login_mode = load_settings().get("login", {}).get("mode", "password_only")
    if login_mode == "feishu_only":
        return respModel().error_resp("Password login is disabled. Please use Feishu login.")

    payload = request.json or {}
    username = payload.get("username", "")
    password = payload.get("password", "")
    user = User.query.filter_by(username=username, password=password).first()
    if not user:
        return respModel().error_resp("Login failed. Please check username and password.")

    token = JwtUtils.create_token(user.access_user_id, user.access_name, user.access_email or "")
    return respModel().ok_resp(
        obj=None,
        msg="Login successful",
        dic_t={
            "token": token,
            "role": user.role,
            "username": user.username,
            "access_name": user.access_name,
            "access_user_id": user.access_user_id,
        },
    )


@module_route.route("/login/config", methods=["GET"])
def login_config():
    settings = load_settings()
    mode = settings.get("login", {}).get("mode", "password_only")
    return respModel().ok_resp_simple(lst={"mode": mode}, msg="ok")
