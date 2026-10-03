from datetime import datetime
import secrets

import requests
from flask import Blueprint, current_app, request

from core.jwtUtil import JwtUtils
from core.resp_model import respModel
from extensions import database
from platformconfig.service.runtime_store import load_settings
from sysmanage.model.user import User

module_route = Blueprint("route_feishulogin", __name__)


def feishu_enabled():
    login_mode = load_settings().get("login", {}).get("mode", "password_only")
    return login_mode in ("feishu_only", "mixed")


@module_route.route("/feishu/config", methods=["GET"])
def feishu_config():
    if not feishu_enabled():
        return respModel().error_resp("Feishu login is disabled.")

    app_id = current_app.config.get("FEISHU_APP_ID")
    if not app_id:
        return respModel().error_resp("FEISHU_APP_ID is not configured.")

    settings = load_settings()
    redirect_uri = settings.get("feishu", {}).get("redirect_uri", "")
    return respModel().ok_resp_simple(lst={"app_id": app_id, "redirect_uri": redirect_uri}, msg="ok")


@module_route.route("/feishu/login", methods=["POST"])
def feishu_login():
    if not feishu_enabled():
        return respModel().error_resp("Feishu login is disabled.")

    code = (request.json or {}).get("code")
    if not code:
        return respModel().error_resp("Missing authorization code.")

    app_id = current_app.config.get("FEISHU_APP_ID")
    app_secret = current_app.config.get("FEISHU_APP_SECRET")
    if not app_id or not app_secret:
        return respModel().error_resp("Feishu API credentials are not configured.")

    token_url = "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal"
    resp = requests.post(token_url, json={"app_id": app_id, "app_secret": app_secret}, timeout=15).json()
    if resp.get("code") != 0:
        return respModel().error_resp("Failed to get Feishu token: " + str(resp.get("msg")))

    app_access_token = resp.get("tenant_access_token")
    user_token_url = "https://open.feishu.cn/open-apis/authen/v1/access_token"
    headers = {"Authorization": f"Bearer {app_access_token}"}
    user_resp = requests.post(
        user_token_url,
        headers=headers,
        json={"grant_type": "authorization_code", "code": code},
        timeout=15,
    ).json()

    if user_resp.get("code") != 0:
        return respModel().error_resp("Failed to get Feishu user info: " + str(user_resp.get("msg")))

    data = user_resp.get("data", {})
    open_id = data.get("open_id")
    name = data.get("name") or data.get("en_name") or "Feishu User"
    email = data.get("email") or ""

    if not open_id:
        return respModel().error_resp("Feishu did not return open_id.")

    settings = load_settings()
    feishu_settings = settings.get("feishu", {})
    user = User.query.filter_by(access_user_id=open_id).first()
    if not user:
        if not feishu_settings.get("auto_register", True):
            return respModel().error_resp("This Feishu account is not registered. Please contact an administrator.")

        username = email or open_id
        if User.query.filter_by(username=username).first():
            username = open_id
        role = "pending" if feishu_settings.get("require_approval", False) else feishu_settings.get("default_role", "user")

        user = User(
            username=username,
            password=secrets.token_urlsafe(32),
            access_name=name,
            access_email=email,
            access_user_id=open_id,
            role=role,
            create_time=datetime.strftime(datetime.today(), "%Y-%m-%d %H:%M:%S"),
        )
        database.session.add(user)
        database.session.commit()
    else:
        user.access_name = name or user.access_name
        user.access_email = email or user.access_email
        database.session.commit()

    if user.role == "pending":
        return respModel().error_resp("Your account is waiting for administrator approval.")

    token = JwtUtils.create_token(user.access_user_id, user.access_name, user.access_email or "")
    login_data = {
        "token": token,
        "username": user.username,
        "access_name": user.access_name,
        "access_user_id": user.access_user_id,
        "role": user.role,
    }
    return respModel().ok_resp(obj=None, msg="Feishu login successful", dic_t=login_data)
