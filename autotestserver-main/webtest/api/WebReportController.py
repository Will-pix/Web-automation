# 用来专门查看报告的
import os

from flask import Blueprint, request, current_app
from core.resp_model import respModel
from extensions import database
from datetime import datetime
from flask import send_from_directory


# 模块信息
module_name = "WebReportViewer"  # 模块名称
module_route = Blueprint(f"route_{module_name}", __name__)

@module_route.route(f'/{module_name}/<path:dir>/<filename>',methods=["GET"])
def report_viewer(dir, filename):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    report_root_dir = current_app.config['WEB_REPORT_ROOT_DIR']
    report_root_dir = os.path.join(current_dir, report_root_dir)
    return send_from_directory(f"{report_root_dir}/{dir}/", filename)