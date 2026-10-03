import os

# 数据库配置 - 请在新环境配置实际的数据库连接
# 示例: 'mysql+pymysql://user:password@localhost:3306/dbname'
SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI", "")

SQLALCHEMY_TRACK_MODIFICATIONS = True
SECRET_KEY = "111222333444"

# AI Configuration - AI模型配置
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
AI_MODEL_NAME = os.environ.get("AI_MODEL_NAME", "doubao-pro-4k")
AI_API_BASE = os.environ.get("AI_API_BASE", "https://ark.cn-beijing.volces.com/api/v3")

# api
CASES_ROOT_DIR = "../testfile"
REPORT_ROOT_DIR = "../report"
API_CLII_DIR = "../tool/apirunner/clii.py"
API_ALLURE_DIR = "allure"
# web
CASES_ROOT_WEB_DIR = "../testfile"
KEY_WORDS_DIR = "../keyswords"
WEB_REPORT_ROOT_DIR = "../report"
WEB_CLI_DIR = "../tool/webrun/cli.py"
# WEB_ALLURE_DIR = "/usr/local/bin/allure"
WEB_ALLURE_DIR = "allure"
# feishu
FEISHU_APP_ID = os.environ.get("FEISHU_APP_ID", "")
FEISHU_APP_SECRET = os.environ.get("FEISHU_APP_SECRET", "")
FEISHU_WEBHOOK_URL = os.environ.get("FEISHU_WEBHOOK_URL", "")

# file
UPLOAD_FOLDER = "../file"