from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT_DIR / "config" / "runtime_settings.json"
DEPLOY_DIR = ROOT_DIR / "easy_deploy"


def default_settings() -> dict[str, Any]:
    return {
        "login": {
            "mode": "password_only",
        },
        "feishu": {
            "app_id": "",
            "app_secret": "",
            "redirect_uri": "",
            "auto_register": True,
            "default_role": "user",
            "require_approval": False,
        },
        "branding": {
            "platform_name": "Web Automation Studio",
            "primary_color": "#1f6feb",
            "accent_color": "#22c55e",
            "support_url": "",
        },
        "ai": {
            "provider_name": "Doubao",
            "api_base": "https://ark.cn-beijing.volces.com/api/v3",
            "api_key": "",
            "model_name": "doubao-pro-4k",
            "request_path": "/chat/completions",
            "vision_model_name": "doubao-1-5-ui-tars-250428",
            "text_model_name": "doubao-seed-1-6-250615",
        },
        "deployment": {
            "backend_port": 8000,
            "frontend_port": 8080,
            "mysql_host": "mysql",
            "mysql_port": 3306,
            "mysql_db": "hcdb",
            "mysql_user": "root",
            "mysql_password": "123456",
            "public_base_url": "",
            "docker_backend_image": "python:3.11-slim",
            "docker_frontend_node_image": "node:18-alpine",
            "docker_frontend_nginx_image": "nginx:1.27-alpine",
        },
        "browser_previews": [
            {"name": "Browser Driver 1", "url": ""},
            {"name": "Browser Driver 2", "url": ""},
            {"name": "Browser Driver 3", "url": ""},
            {"name": "Browser Driver 4", "url": ""},
        ],
        "notification": {
            "platform": "feishu",
            "webhook_url": "",
            "enabled": False,
        },
    }


def load_settings() -> dict[str, Any]:
    settings = default_settings()
    if CONFIG_PATH.exists():
        try:
            stored = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            if isinstance(stored, dict):
                settings = deep_merge(settings, stored)
        except json.JSONDecodeError:
            pass
    return settings


def save_settings(data: dict[str, Any]) -> dict[str, Any]:
    settings = deep_merge(default_settings(), data)
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(
        json.dumps(settings, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return settings


def update_settings(partial: dict[str, Any]) -> dict[str, Any]:
    merged = deep_merge(load_settings(), partial)
    return save_settings(merged)


def deep_merge(base: dict[str, Any], extra: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(base)
    for key, value in extra.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def generate_deploy_bundle(settings: dict[str, Any], *, output_dir: str | None = None) -> dict[str, str]:
    target_dir = Path(output_dir) if output_dir else DEPLOY_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    deployment = settings["deployment"]
    ai = settings["ai"]
    feishu = settings.get("feishu", {})

    env_text = f"""FLASK_ENV=production
SQLALCHEMY_DATABASE_URI=mysql+pymysql://{deployment["mysql_user"]}:{deployment["mysql_password"]}@{deployment["mysql_host"]}:{deployment["mysql_port"]}/{deployment["mysql_db"]}?charset=utf8mb4
OPENAI_API_KEY={ai["api_key"]}
AI_MODEL_NAME={ai["model_name"]}
AI_API_BASE={ai["api_base"]}
FEISHU_APP_ID={feishu.get("app_id", "")}
FEISHU_APP_SECRET={feishu.get("app_secret", "")}
"""

    compose_text = f"""services:
  mysql:
    image: mysql:8.0
    restart: unless-stopped
    environment:
      MYSQL_DATABASE: {deployment["mysql_db"]}
      MYSQL_ROOT_PASSWORD: {deployment["mysql_password"]}
    ports:
      - "{deployment["mysql_port"]}:3306"
    volumes:
      - mysql_data:/var/lib/mysql

  backend:
    build:
      context: ..
    restart: unless-stopped
    env_file:
      - ./.env.easydeploy
    depends_on:
      - mysql
    ports:
      - "{deployment["backend_port"]}:8000"

  frontend:
    build:
      context: ../../autotestweb-main
    restart: unless-stopped
    depends_on:
      - backend
    ports:
      - "{deployment["frontend_port"]}:80"

volumes:
  mysql_data:
"""

    bat_text = """@echo off
setlocal
cd /d %~dp0
docker compose -f docker-compose.easydeploy.yml up -d --build
echo.
echo Easy deploy started.
pause
"""

    sh_text = """#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
docker compose -f docker-compose.easydeploy.yml up -d --build
printf '\\nEasy deploy started.\\n'
"""

    readme_text = f"""# Easy Deploy

Frontend: http://localhost:{deployment["frontend_port"]}
Backend: http://localhost:{deployment["backend_port"]}

1. Edit `.env.easydeploy` if you need to change database or AI settings.
2. Run `start_easy.bat` on Windows or `sh start_easy.sh` on macOS/Linux.
3. Open the frontend URL after the containers are ready.
"""

    files = {
        ".env.easydeploy": env_text,
        "docker-compose.easydeploy.yml": compose_text,
        "start_easy.bat": bat_text,
        "start_easy.sh": sh_text,
        "README.easydeploy.md": readme_text,
    }

    result: dict[str, str] = {}
    for name, content in files.items():
        target = target_dir / name
        target.write_text(content, encoding="utf-8")
        result[name] = str(target)
    return result


def build_public_report_url(execute_uuid: str) -> str:
    settings = load_settings()
    public_base_url = (settings.get("deployment", {}).get("public_base_url") or "").rstrip("/")
    if public_base_url:
      return f"{public_base_url}/api/WebReportViewer/{execute_uuid}/index.html"
    return f"http://127.0.0.1:5000/api/WebReportViewer/{execute_uuid}/index.html"
