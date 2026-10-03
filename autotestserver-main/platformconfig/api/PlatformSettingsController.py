from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess

from flask import Blueprint, current_app, request

from core.resp_model import respModel
from core.auth_decocator import admin_required, jwt_required
from extensions import database
from platformconfig.service.runtime_store import (
    generate_deploy_bundle,
    load_settings,
    update_settings,
)
from platformconfig.service.docx_keyword_parser import extract_keyword_blocks_from_docx
from webtest.model.WebInfoModel import WebInfo
from webtest.model.WebInfoStepModel import WebInfoStep
from webtest.model.WebKeyWordModel import WebKeyWord


module_route = Blueprint("route_platform_settings", __name__)


@module_route.route("/PlatformSettings/profile", methods=["GET"])
@admin_required
def get_profile():
    settings = load_settings()
    settings["diagnostics"] = collect_diagnostics()
    return respModel.ok_resp_simple(lst=settings, msg="ok")


@module_route.route("/PlatformSettings/profile", methods=["PUT"])
@admin_required
def save_profile():
    payload = request.json or {}
    settings = update_settings(payload)
    apply_runtime_ai_config(settings)
    return respModel.ok_resp_simple(lst=settings, msg="saved")


@module_route.route("/PlatformSettings/generateDeployBundle", methods=["POST"])
@admin_required
def generate_bundle():
    payload = request.json or {}
    output_dir = payload.get("output_dir", "").strip()
    settings = load_settings()
    files = generate_deploy_bundle(settings, output_dir=output_dir or None)
    return respModel.ok_resp_simple(
        lst={
            "files": files,
            "settings": settings["deployment"],
        },
        msg="bundle generated",
    )


@module_route.route("/PlatformSettings/runDiagnostics", methods=["POST"])
@admin_required
def run_diagnostics():
    return respModel.ok_resp_simple(lst={"items": collect_deployment_checks()}, msg="diagnostics completed")


@module_route.route("/PlatformSettings/importKeywords", methods=["POST"])
@admin_required
def import_keywords():
    if "file" not in request.files:
        return respModel.error_resp("missing file")

    import_type = request.form.get("import_type", "keyword_code")
    uploaded = request.files["file"]
    filename = uploaded.filename or "keyword.py"

    if import_type == "docx_keywords" or filename.lower().endswith(".docx"):
        return import_docx_keywords(uploaded, request.form)

    content = uploaded.read().decode("utf-8", errors="ignore")

    if import_type == "step_lines":
        return import_step_lines(content, request.form)
    return import_keyword_code(content, filename, request.form)


def import_keyword_code(content: str, filename: str, form) -> object:
    keyword_name = (form.get("name") or Path(filename).stem).strip()
    keyword_fun_name = (form.get("keyword_fun_name") or Path(filename).stem).strip()
    operation_type_id = int(form.get("operation_type_id") or 1)
    is_enabled = form.get("is_enabled", "true")
    keyword_desc = form.get("keyword_desc", "[]")

    record = WebKeyWord.query.filter_by(keyword_fun_name=keyword_fun_name).first()
    if record:
        record.name = keyword_name
        record.keyword_fun_name = keyword_fun_name
        record.keyword_value = content
        record.operation_type_id = operation_type_id
        record.keyword_desc = keyword_desc
        record.is_enabled = is_enabled
        action = "updated"
    else:
        record = WebKeyWord(
            name=keyword_name,
            keyword_fun_name=keyword_fun_name,
            keyword_value=content,
            operation_type_id=operation_type_id,
            keyword_desc=keyword_desc,
            is_enabled=is_enabled,
        )
        database.session.add(record)
        action = "created"

    database.session.commit()
    return respModel.ok_resp_simple(
        lst={
            "action": action,
            "keyword_id": record.id,
            "keyword_fun_name": keyword_fun_name,
        },
        msg="keyword imported",
    )


def import_step_lines(content: str, form) -> object:
    web_info_id = int(form.get("web_info_id") or 0)
    keyword_id = int(form.get("key_word_id") or 0)

    if web_info_id <= 0 or keyword_id <= 0:
        return respModel.error_resp("web_info_id and key_word_id are required")

    web_info = WebInfo.query.filter_by(id=web_info_id).first()
    if not web_info:
        return respModel.error_resp("target case not found")

    lines = parse_lines(content)
    if not lines:
        return respModel.error_resp("no valid lines found")

    current_max = database.session.query(database.func.max(WebInfoStep.run_order)).filter_by(
        web_info_id=web_info_id
    ).scalar() or 0

    created_ids = []
    for index, line in enumerate(lines, start=1):
        step = WebInfoStep(
            web_info_id=web_info_id,
            key_word_id=keyword_id,
            step_desc=f"Imported Step {index}",
            ref_variable=json.dumps({"ai_step": line}, ensure_ascii=False),
            run_order=current_max + index * 10,
            is_enabled=True,
        )
        database.session.add(step)
        database.session.flush()
        created_ids.append(step.id)

    database.session.commit()
    return respModel.ok_resp_simple(
        lst={
            "created_count": len(created_ids),
            "created_ids": created_ids,
        },
        msg="steps imported",
    )


def import_docx_keywords(uploaded, form) -> object:
    temp_dir = Path(current_app.root_path).parent / "tmp" / "docx_imports"
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_path = temp_dir / (uploaded.filename or "keywords.docx")
    uploaded.save(temp_path)

    blocks = extract_keyword_blocks_from_docx(temp_path)
    if not blocks:
        return respModel.error_resp("no keyword classes found in docx")

    operation_type_id = int(form.get("operation_type_id") or 1)
    is_enabled = form.get("is_enabled", "true")

    imported = []
    for block in blocks:
        record = WebKeyWord.query.filter_by(keyword_fun_name=block["keyword_fun_name"]).first()
        if record:
            record.name = block["name"]
            record.keyword_value = block["keyword_value"]
            record.keyword_desc = block["keyword_desc"]
            record.operation_type_id = operation_type_id
            record.is_enabled = is_enabled
            action = "updated"
        else:
            record = WebKeyWord(
                name=block["name"],
                keyword_fun_name=block["keyword_fun_name"],
                keyword_value=block["keyword_value"],
                keyword_desc=block["keyword_desc"],
                operation_type_id=operation_type_id,
                is_enabled=is_enabled,
            )
            database.session.add(record)
            action = "created"
        database.session.flush()
        imported.append(
            {
                "id": record.id,
                "name": block["name"],
                "keyword_fun_name": block["keyword_fun_name"],
                "action": action,
            }
        )

    database.session.commit()
    return respModel.ok_resp_simple(
        lst={
            "count": len(imported),
            "items": imported,
        },
        msg="docx keywords imported",
    )


def parse_lines(content: str) -> list[str]:
    text = content.strip()
    if not text:
        return []

    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return [str(item).strip() for item in parsed if str(item).strip()]
    except json.JSONDecodeError:
        pass

    return [line.strip() for line in text.splitlines() if line.strip()]


def apply_runtime_ai_config(settings) -> None:
    ai = settings.get("ai", {})
    if ai:
        current_app.config["OPENAI_API_KEY"] = ai.get("api_key", "")
        current_app.config["AI_MODEL_NAME"] = ai.get("model_name", "")
        current_app.config["AI_API_BASE"] = ai.get("api_base", "")
    feishu = settings.get("feishu", {})
    if feishu:
        current_app.config["FEISHU_APP_ID"] = feishu.get("app_id", "") or current_app.config.get("FEISHU_APP_ID", "")
        current_app.config["FEISHU_APP_SECRET"] = feishu.get("app_secret", "") or current_app.config.get("FEISHU_APP_SECRET", "")
    notification = settings.get("notification", {})
    webhook_url = notification.get("webhook_url", "")
    if webhook_url:
        current_app.config["FEISHU_WEBHOOK_URL"] = webhook_url


def collect_diagnostics():
    issues = []

    try:
        postgres_refs = database.session.execute(
            database.text(
                "SELECT COUNT(*) AS total FROM t_web_database WHERE db_type IN ('PostgreSQL', 'postgres', 'postgresql')"
            )
        ).scalar()
        if postgres_refs:
            issues.append(
                {
                    "level": "warning",
                    "title": "PostgreSQL references still exist",
                    "detail": f"{postgres_refs} database connection records still point to PostgreSQL.",
                }
            )
    except Exception as exc:
        issues.append(
            {
                "level": "warning",
                "title": "Database diagnostics unavailable",
                "detail": f"Could not inspect database compatibility: {exc}",
            }
        )

    settings = load_settings()
    if not settings["ai"].get("api_key"):
        issues.append(
            {
                "level": "info",
                "title": "AI API Key not configured",
                "detail": "Set the API Key in Platform Settings before using AI-driven actions.",
            }
        )

    login_mode = settings.get("login", {}).get("mode", "password_only")
    feishu = settings.get("feishu", {})
    if login_mode in ("feishu_only", "mixed") and not feishu.get("app_id"):
        issues.append(
            {
                "level": "warning",
                "title": "Feishu App ID not configured",
                "detail": "Set Feishu App ID and App Secret before enabling Feishu login.",
            }
        )

    return issues


def make_check(name, status, detail):
    return {"name": name, "status": status, "detail": detail}


def collect_deployment_checks():
    checks = []
    settings = load_settings()

    try:
        database.session.execute(database.text("SELECT 1")).scalar()
        checks.append(make_check("数据库连接", "pass", "数据库连接正常。"))
    except Exception as exc:
        checks.append(make_check("数据库连接", "fail", f"数据库连接失败：{exc}"))

    login_mode = settings.get("login", {}).get("mode", "password_only")
    feishu = settings.get("feishu", {})
    if login_mode in ("feishu_only", "mixed"):
        if feishu.get("app_id") and feishu.get("app_secret"):
            checks.append(make_check("飞书登录配置", "pass", "已配置 App ID 和 App Secret。"))
        else:
            checks.append(make_check("飞书登录配置", "fail", "当前登录模式启用了飞书，但 App ID 或 App Secret 未配置。"))
        if feishu.get("redirect_uri"):
            checks.append(make_check("飞书回调地址", "pass", f"当前回调地址：{feishu.get('redirect_uri')}"))
        else:
            checks.append(make_check("飞书回调地址", "warning", "未填写回调地址，将使用前端当前地址 + /login。"))
    else:
        checks.append(make_check("飞书登录配置", "warning", "当前登录模式未启用飞书登录。"))

    ai = settings.get("ai", {})
    if ai.get("api_key") and ai.get("api_base") and ai.get("model_name"):
        checks.append(make_check("AI 配置", "pass", "AI API Base、模型名和 API Key 已配置。"))
    else:
        checks.append(make_check("AI 配置", "warning", "AI 配置不完整，AI 关键字可能不可用。"))

    notification = settings.get("notification", {})
    if notification.get("enabled") and not notification.get("webhook_url"):
        checks.append(make_check("通知配置", "fail", "通知已启用，但 Webhook URL 为空。"))
    elif notification.get("webhook_url"):
        checks.append(make_check("通知配置", "pass", "Webhook URL 已配置。"))
    else:
        checks.append(make_check("通知配置", "warning", "通知未启用。"))

    report_dir = Path(current_app.root_path) / current_app.config.get("WEB_REPORT_ROOT_DIR", "../report")
    upload_dir = Path(current_app.root_path) / current_app.config.get("UPLOAD_FOLDER", "../file")
    for label, target in [("报告目录", report_dir), ("上传目录", upload_dir)]:
        try:
            target.mkdir(parents=True, exist_ok=True)
            test_file = target / ".write_test"
            test_file.write_text("ok", encoding="utf-8")
            test_file.unlink(missing_ok=True)
            checks.append(make_check(label, "pass", f"{target} 可写。"))
        except Exception as exc:
            checks.append(make_check(label, "fail", f"{target} 不可写：{exc}"))

    allure_cmd = current_app.config.get("WEB_ALLURE_DIR", "allure")
    allure_path = shutil.which(allure_cmd) or (allure_cmd if Path(allure_cmd).exists() else "")
    if allure_path:
        try:
            result = subprocess.run([allure_cmd, "--version"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                checks.append(make_check("Allure 命令", "pass", f"Allure 可用：{result.stdout.strip()}"))
            else:
                checks.append(make_check("Allure 命令", "warning", result.stderr.strip() or "Allure 命令返回非 0 状态。"))
        except Exception as exc:
            checks.append(make_check("Allure 命令", "warning", f"找到 Allure 但执行失败：{exc}"))
    else:
        checks.append(make_check("Allure 命令", "fail", "未找到 Allure 命令，测试报告生成可能失败。"))

    public_base_url = settings.get("deployment", {}).get("public_base_url")
    if public_base_url:
        checks.append(make_check("报告公开地址", "pass", f"已配置：{public_base_url}"))
    else:
        checks.append(make_check("报告公开地址", "warning", "未配置 public_base_url，报告链接可能回落到 127.0.0.1。"))

    if os.getenv("FLASK_ENV", "development") == "production" and current_app.config.get("SECRET_KEY") == "111222333444":
        checks.append(make_check("SECRET_KEY", "fail", "生产环境仍在使用默认 SECRET_KEY。"))
    else:
        checks.append(make_check("SECRET_KEY", "pass", "SECRET_KEY 未命中默认弱值。"))

    return checks


@module_route.route("/PlatformSettings/testNotification", methods=["POST"])
@admin_required
def test_notification():
    import requests as http_requests
    payload = request.json or {}
    platform = payload.get("platform", "feishu")
    webhook_url = payload.get("webhook_url", "")

    if not webhook_url:
        return respModel.error_resp("webhook_url is required")

    if platform == "feishu":
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        body = {
            "msg_type": "interactive",
            "card": {
                "schema": "2.0",
                "body": {
                    "direction": "vertical",
                    "padding": "12px",
                    "elements": [
                        {
                            "tag": "markdown",
                            "content": f"这是一条测试通知\n发送时间：{timestamp}\n如果您看到这条消息，说明 Webhook 配置正确 ✅",
                            "text_align": "left",
                            "text_size": "normal_v2",
                        }
                    ],
                },
                "header": {
                    "title": {"tag": "plain_text", "content": "Web自动化平台 - 通知测试"},
                    "template": "blue",
                },
            },
        }
        headers = {"Content-Type": "application/json"}
        try:
            resp = http_requests.post(webhook_url, headers=headers, json=body, timeout=10)
            if resp.status_code == 200:
                return respModel.ok_resp_simple(lst={"status": "sent"}, msg="测试通知已发送")
            else:
                return respModel.error_resp(f"发送失败，状态码: {resp.status_code}")
        except Exception as e:
            return respModel.error_resp(f"发送异常: {e}")

    return respModel.error_resp(f"暂不支持平台: {platform}")
