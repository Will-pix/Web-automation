import re
from datetime import datetime

from flask import Blueprint, request
from core.resp_model import respModel
from extensions import database
from webtest.model.WebHistoryModel import WebHistoryModel
from webtest.model.WebHistoryTimeModel import WebHistoryTimeModel
from webtest.model.WebCollectionInfoModel import WebCollectionInfo
from webtest.model.WebProjectModel import WebProject

module_name = "Workbench"
module_route = Blueprint(f"route_{module_name}", __name__)


def _parse_history_desc(desc):
    """解析 history_desc 中的数字，返回 (total, passed, failed)"""
    desc = desc or ""
    total_match = re.search(r'总数:(\d+)', desc)
    passed_match = re.search(r'通过(\d+)', desc)
    failed_match = re.search(r'失败(\d+)', desc)
    total = int(total_match.group(1)) if total_match else 0
    passed = int(passed_match.group(1)) if passed_match else 0
    failed = int(failed_match.group(1)) if failed_match else 0
    return total, passed, failed


@module_route.route(f"/{module_name}/getExecutionRecords", methods=["POST"])
def getExecutionRecords():
    """获取工作台执行记录列表（手动+定时任务合并）"""
    try:
        page = int(request.json.get("page", 1))
        page_size = int(request.json.get("pageSize", 10))
        trigger_type = request.json.get("trigger_type", "")  # "" 全部 / "手动执行" / "定时任务"

        base_cols = [
            WebHistoryModel.id,
            WebHistoryModel.collection_info_id,
            WebHistoryModel.history_desc,
            WebHistoryModel.history_detail,
            WebHistoryModel.create_time,
            WebHistoryModel.collection_principal,
            WebHistoryModel.collection_env_type,
            WebHistoryModel.run_time,
            WebCollectionInfo.collection_name,
            WebProject.project_name,
        ]

        all_records = []

        if trigger_type != "定时任务":
            manual_records = database.session.query(
                *base_cols,
                database.literal("手动执行").label("trigger_type"),
                database.literal(None).label("task_id"),
            ).outerjoin(
                WebCollectionInfo, WebHistoryModel.collection_info_id == WebCollectionInfo.id
            ).outerjoin(
                WebProject, WebCollectionInfo.project_id == WebProject.id
            ).all()
            all_records.extend(manual_records)

        if trigger_type != "手动执行":
            timed_records = database.session.query(
                WebHistoryTimeModel.id,
                WebHistoryTimeModel.collection_info_id,
                WebHistoryTimeModel.history_desc,
                WebHistoryTimeModel.history_detail,
                WebHistoryTimeModel.create_time,
                WebHistoryTimeModel.collection_principal,
                WebHistoryTimeModel.collection_env_type,
                WebHistoryTimeModel.run_time,
                WebCollectionInfo.collection_name,
                WebProject.project_name,
                database.literal("定时任务").label("trigger_type"),
                WebHistoryTimeModel.task_id,
            ).outerjoin(
                WebCollectionInfo, WebHistoryTimeModel.collection_info_id == WebCollectionInfo.id
            ).outerjoin(
                WebProject, WebCollectionInfo.project_id == WebProject.id
            ).all()
            all_records.extend(timed_records)

        all_records.sort(key=lambda r: r.create_time or "", reverse=True)

        total = len(all_records)

        # 分页
        start = (page - 1) * page_size
        end = start + page_size
        page_records = all_records[start:end]

        # 构建记录列表
        records = []
        for r in page_records:
            total_c, passed_c, failed_c = _parse_history_desc(r.history_desc)
            records.append({
                "id": r.id,
                "collection_info_id": r.collection_info_id,
                "collection_name": r.collection_name or "未知集合",
                "project_name": r.project_name or "未知项目",
                "history_desc": r.history_desc or "",
                "history_detail": r.history_detail,
                "create_time": r.create_time.strftime("%Y-%m-%d %H:%M:%S") if r.create_time else "",
                "collection_principal": r.collection_principal or "",
                "collection_env_type": r.collection_env_type or "common",
                "run_time": r.run_time or "",
                "trigger_type": r.trigger_type,
                "task_id": r.task_id,
                "total_count": total_c,
                "passed_count": passed_c,
                "failed_count": failed_c,
                "status": "passed" if failed_c == 0 else "failed",
            })

        # 今日汇总
        today_str = datetime.today().strftime("%Y-%m-%d")
        today_executions = 0
        today_passed = 0
        today_failed = 0
        today_cases = 0
        for r in all_records:
            if r.create_time and r.create_time.strftime("%Y-%m-%d") == today_str:
                today_executions += 1
                total_c, passed_c, failed_c = _parse_history_desc(r.history_desc)
                today_cases += total_c
                if failed_c == 0:
                    today_passed += 1
                else:
                    today_failed += 1

        summary = {
            "today_executions": today_executions,
            "today_passed": today_passed,
            "today_failed": today_failed,
            "today_cases": today_cases,
            "total_executions": total,
        }

        return respModel.ok_resp_simple_list(
            lst={"records": records, "summary": summary},
            total=total,
            msg="查询成功"
        )

    except Exception as e:
        print(e)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")
