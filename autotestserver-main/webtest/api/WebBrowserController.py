from datetime import datetime
import json
from pathlib import Path
import time

import requests
from flask import Blueprint, request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as Chrome_Service
from selenium.webdriver.common.options import ArgOptions
from selenium.webdriver.firefox.service import Service as Firefox_Service
from selenium.webdriver.ie.service import Service as Ie_Service
from selenium.webdriver.remote.remote_connection import RemoteConnection

from core.auth_decocator import jwt_required
from core.resp_model import respModel
from extensions import database
from webtest.model.WebBrowserModel import WebBrowser


module_name = "WebBrowser"
module_model = WebBrowser
module_route = Blueprint(f"route_{module_name}", __name__)


def browser_check(name, status, detail):
    return {"name": name, "status": status, "detail": detail}


def parse_browser_capability(browser_info):
    capability = {"browserName": browser_info.enName}
    browser_debug = (browser_info.browser_debug or "").strip()
    if browser_debug:
        capability.update(json.loads(browser_debug))
    return capability


def build_browser_options(capability):
    options = ArgOptions()
    for key, value in capability.items():
        options.set_capability(key, value)
    return options


@module_route.route(f"/{module_name}/queryByPage", methods=["POST"])
def queryByPage():
    try:
        page = int(request.json["page"])
        page_size = int(request.json["pageSize"])
        filter_list = []

        project_id = request.json.get("project_id", 0)
        if type(project_id) is not str and project_id > 0:
            filter_list.append(module_model.project_id == project_id)

        module_id = request.json.get("module_id", 0)
        if type(module_id) is not str and module_id > 0:
            filter_list.append(module_model.module_id == module_id)

        name = request.json.get("name", "")
        if len(name) > 0:
            filter_list.append(module_model.name.like(f"%{name}%"))

        create_by = request.json.get("create_by")
        if create_by:
            filter_list.append(module_model.create_by == create_by)

        update_by = request.json.get("update_by")
        if update_by:
            filter_list.append(module_model.update_by == update_by)

        datas = (
            module_model.query.filter(*filter_list)
            .order_by(module_model.create_time.desc())
            .limit(page_size)
            .offset((page - 1) * page_size)
            .all()
        )
        total = module_model.query.filter(*filter_list).count()
        return respModel().ok_resp_list(lst=datas, total=total)
    except Exception as e:
        print(e)
        return respModel.error_resp(f"服务器错误，请联系管理员:{e}")


@module_route.route(f"/{module_name}/queryById", methods=["GET"])
def queryById():
    try:
        data_id = int(request.args.get("id"))
        data = module_model.query.filter_by(id=data_id).first()
        if data:
            return respModel().ok_resp(obj=data)
        return respModel.ok_resp(msg="查询成功,但是没有数据")
    except Exception as e:
        print(e)
        return respModel.error_resp(f"服务器错误，请联系管理员:{e}")


@module_route.route(f"/{module_name}/insert", methods=["POST"])
def insert():
    try:
        request.json["id"] = None
        for field in ("remote_url", "driver_path", "enName", "browser_debug"):
            if field in request.json and isinstance(request.json[field], str):
                request.json[field] = request.json[field].strip()
        data = module_model(**request.json, create_time=datetime.strftime(datetime.today(), "%Y-%m-%d %H:%M:%S"))
        database.session.add(data)
        database.session.flush()
        data_id = data.id
        database.session.commit()
        return respModel.ok_resp(msg="添加成功", dic_t={"id": data_id})
    except Exception as e:
        print(e)
        return respModel.error_resp(msg=f"添加失败:{e}")


@module_route.route(f"/{module_name}/update", methods=["PUT"])
def update():
    try:
        update_data = request.json
        for field in ("remote_url", "driver_path", "enName", "browser_debug"):
            if field in update_data and isinstance(update_data[field], str):
                update_data[field] = update_data[field].strip()
        target_data = module_model.query.filter_by(id=update_data["id"]).first()
        if target_data:
            for key, value in update_data.items():
                if key != "id":
                    setattr(target_data, key, value)
        database.session.commit()
        return respModel.ok_resp(msg="修改成功")
    except Exception as e:
        print(e)
        return respModel.error_resp(msg=f"修改失败，请联系管理员{e}")


@module_route.route(f"/{module_name}/delete", methods=["DELETE"])
def delete():
    try:
        module_model.query.filter_by(id=request.args.get("id")).delete()
        database.session.commit()
        return respModel.ok_resp(msg="删除成功")
    except Exception as e:
        print(e)
        return respModel.error_resp(msg=f"服务器错误，删除失败：{e}")


@module_route.route(f"/{module_name}/testConnection", methods=["POST"])
@jwt_required
def test_connection():
    payload = request.json or {}
    browser_id = payload.get("id")
    browser_info = module_model.query.filter_by(id=browser_id).first() if browser_id else None
    if not browser_info:
        return respModel.error_resp("browser record not found")

    checks = []
    driver = None
    started_at = time.time()

    try:
        capability = parse_browser_capability(browser_info)
        browser_name = (capability.get("browserName") or "").lower()
        if browser_name not in ("chrome", "firefox", "ie"):
            checks.append(browser_check("浏览器类型", "fail", "浏览器类型必须是 chrome、firefox 或 ie。"))
            return respModel.ok_resp_simple(lst={"items": checks}, msg="browser check completed")

        checks.append(browser_check("浏览器类型", "pass", f"浏览器类型：{browser_name}"))
        checks.append(browser_check("调试参数 JSON", "pass", "browser_debug 是合法 JSON 或为空。"))

        options = build_browser_options(capability)
        grid_url = (browser_info.remote_url or "").strip()
        driver_path = (browser_info.driver_path or "").strip()

        if grid_url:
            status_url = grid_url.rstrip("/")
            if status_url.endswith("/wd/hub"):
                status_url = status_url[:-7]
            status_url = status_url.rstrip("/") + "/status"
            try:
                status_resp = requests.get(status_url, timeout=5)
                checks.append(
                    browser_check(
                        "Grid 状态接口",
                        "pass" if status_resp.status_code < 500 else "warning",
                        f"{status_url} 返回 HTTP {status_resp.status_code}。",
                    )
                )
            except Exception as exc:
                checks.append(browser_check("Grid 状态接口", "warning", f"状态接口不可访问：{exc}"))

            RemoteConnection.set_timeout(20)
            driver = webdriver.Remote(command_executor=grid_url, options=options)
            checks.append(browser_check("创建远程 Session", "pass", f"Session 创建成功：{driver.session_id}"))
        elif driver_path:
            path = Path(driver_path)
            if not path.exists():
                checks.append(browser_check("驱动路径", "fail", f"驱动文件不存在：{driver_path}"))
                return respModel.ok_resp_simple(lst={"items": checks}, msg="browser check completed")
            checks.append(browser_check("驱动路径", "pass", f"驱动文件存在：{driver_path}"))

            driver_class = {
                "chrome": {"driver": webdriver.Chrome, "service": Chrome_Service},
                "firefox": {"driver": webdriver.Firefox, "service": Firefox_Service},
                "ie": {"driver": webdriver.Ie, "service": Ie_Service},
            }
            driver = driver_class[browser_name]["driver"](
                service=driver_class[browser_name]["service"](driver_path),
                options=options,
            )
            checks.append(browser_check("创建本机 Session", "pass", f"Session 创建成功：{driver.session_id}"))
        else:
            checks.append(
                browser_check(
                    "启动方式",
                    "warning",
                    "未填写远程 Grid 地址或驱动路径，将尝试使用服务器本机默认浏览器驱动。",
                )
            )
            driver_class = {"chrome": webdriver.Chrome, "firefox": webdriver.Firefox, "ie": webdriver.Ie}
            driver = driver_class[browser_name](options=options)
            checks.append(browser_check("创建默认 Session", "pass", f"Session 创建成功：{driver.session_id}"))

        checks.append(browser_check("耗时", "pass", f"{time.time() - started_at:.2f} 秒"))
        return respModel.ok_resp_simple(lst={"items": checks}, msg="browser check completed")
    except json.JSONDecodeError as exc:
        checks.append(browser_check("调试参数 JSON", "fail", f"browser_debug 不是合法 JSON：{exc}"))
        return respModel.ok_resp_simple(lst={"items": checks}, msg="browser check completed")
    except Exception as exc:
        checks.append(browser_check("创建浏览器 Session", "fail", str(exc)))
        return respModel.ok_resp_simple(lst={"items": checks}, msg="browser check completed")
    finally:
        if driver is not None:
            try:
                driver.quit()
            except Exception:
                pass
