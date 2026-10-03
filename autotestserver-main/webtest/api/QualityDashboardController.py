
from flask import Blueprint, request
from core.resp_model import respModel
from extensions import database
from webtest.model.WebHistoryTimeModel import WebHistoryTimeModel
from webtest.model.WebCollectionInfoModel import WebCollectionInfo
from webtest.model.WebInfoModel import WebInfo
from webtest.model.WebProjectModel import WebProject
from sysmanage.model.user import User
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta
import json
import os
import requests
from webtest.keyswords.ai_runtime import get_runtime_ai_settings


# 模块信息
module_name = "QualityDashboard"
module_route = Blueprint(f"route_{module_name}", __name__)


# ==================== 辅助函数：Allure报告失败详情提取 ====================

def extract_allure_failure_details(execute_uuid):
    """
    从Allure报告中提取失败用例的详细信息
    
    参数：
    - execute_uuid: 执行UUID（对应 history_detail 字段）
    
    返回：
    - dict: {case_name: failure_details} 映射
    """
    failure_map = {}
    
    try:
        # 构建Allure报告目录路径
        report_data_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "../report",
            f"{execute_uuid}-data"
        )
        
        if not os.path.exists(report_data_path):
            print(f"[WARN] Allure报告目录不存在: {report_data_path}")
            return failure_map
        
        print(f"[DEBUG] 从Allure报告提取失败详情: {report_data_path}")
        
        # 遍历所有 result.json 文件
        for root, _, files in os.walk(report_data_path):
            for file in files:
                if file.endswith("-result.json"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        # 只处理失败的用例
                        status = data.get("status", "unknown")
                        if status == "passed":
                            continue
                        
                        # 获取用例名称（优先从label）
                        case_name = None
                        labels = data.get("labels", [])
                        for label in labels:
                            if label.get("name") == "case_name":
                                case_name = label.get("value")
                                break
                        if not case_name:
                            case_name = data.get("name", "未知")
                        
                        # 提取失败详情
                        failure_details = extract_failure_info_from_result(data)
                        failure_map[case_name] = failure_details
                        
                    except Exception as e:
                        print(f"[ERROR] 解析Allure文件 {file_path} 失败: {e}")
        
        print(f"[DEBUG] 提取了 {len(failure_map)} 个失败用例的详情")
        
    except Exception as e:
        print(f"[ERROR] 提取Allure失败详情时出错: {e}")
        import traceback
        traceback.print_exc()
    
    return failure_map


def extract_failure_info_from_result(result_data):
    """
    从单个Allure result.json中提取失败详情
    
    返回字段：
    - error_type: 错误类型（AssertionError、TimeoutException、NoSuchElementException等）
    - error_message: 完整错误信息
    - error_trace_summary: 错误堆栈摘要
    - failed_step_name: 失败步骤名称
    - failed_step_index: 失败步骤索引（第几步）
    - total_steps: 总步骤数
    """
    failure_info = {}
    
    try:
        # 1. 提取错误类型和消息
        status_details = result_data.get("statusDetails", {})
        error_message = status_details.get("message", "")
        error_trace = status_details.get("trace", "")
        
        # 错误类型：从message第一行提取（如 "AssertionError"）
        error_type = error_message.split(":")[0].strip() if error_message else "Unknown"
        failure_info["error_type"] = error_type
        
        # 错误摘要：message的完整内容（可能包含元素定位符、超时时间等关键信息）
        failure_info["error_message"] = error_message[:500] if error_message else "无错误信息"  # 限制500字符
        
        # 从trace中提取关键错误行（最后3行通常最重要）
        if error_trace:
            trace_lines = [line.strip() for line in error_trace.split('\n') if line.strip()]
            # 提取最后几行（通常包含实际出错位置）
            key_trace = '\n'.join(trace_lines[-3:]) if len(trace_lines) > 3 else error_trace
            failure_info["error_trace_summary"] = key_trace[:300]  # 限制300字符
        else:
            failure_info["error_trace_summary"] = ""
        
        # 2. 分析失败步骤
        steps = result_data.get("steps", [])
        failure_info["total_steps"] = len(steps)
        
        failed_step_index = -1
        failed_step_name = ""
        
        for idx, step in enumerate(steps):
            if step.get("status") in ["failed", "broken"]:
                failed_step_index = idx + 1  # 从1开始计数
                failed_step_name = step.get("name", "未知步骤")
                
                # 如果步骤也有错误详情，优先使用
                step_details = step.get("statusDetails", {})
                if step_details and not error_message:
                    failure_info["error_message"] = step_details.get("message", "")[:500]
                break
        
        failure_info["failed_step_index"] = failed_step_index
        failure_info["failed_step_name"] = failed_step_name if failed_step_name else "用例级别失败"
        
    except Exception as e:
        print(f"[WARN] 提取单个用例失败详情时出错: {e}")
        failure_info = {
            "error_type": "Unknown",
            "error_message": "无法提取错误信息",
            "error_trace_summary": "",
            "failed_step_name": "未知",
            "failed_step_index": -1,
            "total_steps": 0
        }
    
    return failure_info


# ==================== 质量大盘接口 ====================

@module_route.route(f"/{module_name}/getQualityData", methods=["POST"])
def get_quality_data():
    """
    质量大盘数据统计接口
    筛选维度：日期范围、项目筛选、用例负责人、集合负责人、环境类型
    """
    try:
        # 获取筛选参数
        params = request.json
        start_date = params.get("start_date")  # 格式：YYYY-MM-DD
        end_date = params.get("end_date")      # 格式：YYYY-MM-DD
        project_ids = params.get("project_ids", [])  # 项目ID列表
        case_principals = params.get("case_principals", [])  # 用例负责人ID列表
        collection_principals = params.get("collection_principals", [])  # 集合负责人ID列表
        collection_env_types = params.get("collection_env_type", [])  # 环境类型列表：common/test/stage/online

        # 构建基础查询过滤条件
        filter_list = []
        
        # 日期范围筛选
        if start_date:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            filter_list.append(WebHistoryTimeModel.create_time >= start_datetime)
        if end_date:
            end_datetime = datetime.strptime(end_date + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
            filter_list.append(WebHistoryTimeModel.create_time <= end_datetime)
        
        # 集合负责人筛选
        if collection_principals and len(collection_principals) > 0:
            filter_list.append(WebHistoryTimeModel.collection_principal.in_(collection_principals))
        
        # 环境类型筛选
        if collection_env_types and len(collection_env_types) > 0:
            filter_list.append(WebHistoryTimeModel.collection_env_type.in_(collection_env_types))
        
        # 获取基础历史记录数据
        history_records = WebHistoryTimeModel.query.filter(*filter_list).all()
        
        # 如果需要按项目筛选或用例负责人筛选，需要进一步过滤
        if project_ids and len(project_ids) > 0:
            # 获取符合项目条件的collection_info_id
            valid_collection_ids = [c.id for c in WebCollectionInfo.query.filter(
                WebCollectionInfo.project_id.in_(project_ids)
            ).all()]
            history_records = [r for r in history_records if r.collection_info_id in valid_collection_ids]
        
        # 用例负责人筛选（需要解析 pass_cases_detail 和 failed_cases_detail）
        if case_principals and len(case_principals) > 0:
            filtered_records = []
            for record in history_records:
                has_match = False
                
                # 检查通过的用例
                if hasattr(record, 'pass_cases_detail') and record.pass_cases_detail:
                    try:
                        pass_cases = json.loads(record.pass_cases_detail)
                        has_match = any(
                            case.get("principal") in case_principals 
                            for case in pass_cases
                        )
                    except:
                        pass
                
                # 检查失败的用例
                if not has_match and record.failed_cases_detail:
                    try:
                        failed_cases = json.loads(record.failed_cases_detail)
                        has_match = any(
                            case.get("principal") in case_principals 
                            for case in failed_cases
                        )
                    except:
                        pass
                
                if has_match:
                    filtered_records.append(record)
            
            history_records = filtered_records
        
        # =========================
        # 1. 概览指标统计
        # =========================
        # 解析history_desc字段，格式为："总数:5,通过4,失败1"
        def parse_history_desc(desc):
            """解析历史描述，返回(总数, 通过数, 失败数)"""
            if not desc:
                return 0, 0, 0
            try:
                import re
                total = re.search(r'总数[：:]\s*(\d+)', desc)
                success = re.search(r'通过\s*(\d+)', desc)
                failed = re.search(r'失败\s*(\d+)', desc)
                
                total_num = int(total.group(1)) if total else 0
                success_num = int(success.group(1)) if success else 0
                failed_num = int(failed.group(1)) if failed else 0
                
                return total_num, success_num, failed_num
            except Exception as e:
                print(f"解析history_desc失败: {desc}, 错误: {e}")
                return 0, 0, 0
        
        # 总执行集合数量（记录总数）
        total_executions = len(history_records)
        total_success = 0  # 总通过的用例数量
        total_failed = 0   # 总失败的用例数量
        total_cases = 0    # 总用例数量
        
        for record in history_records:
            total_num, success_num, failed_num = parse_history_desc(record.history_desc)
            total_success += success_num
            total_failed += failed_num
            total_cases += total_num
        
        success_rate = round(total_success / total_cases * 100, 2) if total_cases > 0 else 0
        
        overview_data = {
            "total_executions": total_executions,
            "total_cases": total_cases,
            "total_success": total_success,
            "total_failed": total_failed,
            "success_rate": success_rate
        }
        
        # =========================
        # 2. 负责人维度分布
        # =========================
        # 2.1 用例负责人统计
        # 直接从 t_web_time_history 表的 pass_cases_detail 和 failed_cases_detail 字段统计
        # 统计每个负责人的用例执行次数（累加，不去重）
        case_principal_stats = {}
        
        for record in history_records:
            # 统计通过的用例
            if hasattr(record, 'pass_cases_detail') and record.pass_cases_detail:
                try:
                    pass_cases = json.loads(record.pass_cases_detail)
                    for case in pass_cases:
                        principal_id = case.get("principal", "无")
                        if principal_id not in case_principal_stats:
                            case_principal_stats[principal_id] = {
                                "principal_id": principal_id,
                                "success_count": 0,
                                "failed_count": 0
                            }
                        case_principal_stats[principal_id]["success_count"] += 1
                except Exception as e:
                    print(f"解析 pass_cases_detail 失败: {e}")
            
            # 统计失败的用例
            if record.failed_cases_detail:
                try:
                    failed_cases = json.loads(record.failed_cases_detail)
                    for case in failed_cases:
                        principal_id = case.get("principal", "无")
                        if principal_id not in case_principal_stats:
                            case_principal_stats[principal_id] = {
                                "principal_id": principal_id,
                                "success_count": 0,
                                "failed_count": 0
                            }
                        case_principal_stats[principal_id]["failed_count"] += 1
                except Exception as e:
                    print(f"解析 failed_cases_detail 失败: {e}")
        
        # 转换用例负责人数据并获取用户名
        case_principal_distribution = []
        for principal_id, stats in case_principal_stats.items():
            # 获取用户名
            user = User.query.filter_by(access_user_id=principal_id).first()
            principal_name = user.access_name if user else principal_id
            
            case_count = stats["success_count"] + stats["failed_count"]
            success_rate_case = round(stats["success_count"] / case_count * 100, 2) if case_count > 0 else 0
            
            case_principal_distribution.append({
                "principal_id": principal_id,
                "principal_name": principal_name,
                "case_count": case_count,
                "success_count": stats["success_count"],
                "failed_count": stats["failed_count"],
                "success_rate": success_rate_case
            })
        
        # 2.2 集合负责人统计（集合维度：关注集合执行的成功/失败，不关注用例维度）
        collection_principal_stats = {}
        for record in history_records:
            principal_id = record.collection_principal
            if not principal_id:
                principal_id = "无"
                
            if principal_id not in collection_principal_stats:
                collection_principal_stats[principal_id] = {
                    "principal_id": principal_id,
                    "collection_count": 0,  # 总执行次数
                    "success_count": 0,     # 完全成功的执行次数（失败=0）
                    "failed_count": 0       # 有失败的执行次数（失败>0）
                }
            
            # 集合执行次数累加
            collection_principal_stats[principal_id]["collection_count"] += 1
            
            # 基于 failed_cases_detail 判断集合执行是否成功
            # 如果 failed_cases_detail 为空或没有失败用例，则集合成功
            has_failure = False
            if record.failed_cases_detail:
                try:
                    failed_cases = json.loads(record.failed_cases_detail)
                    has_failure = len(failed_cases) > 0
                except:
                    pass
            
            if not has_failure:
                # 没有失败用例，说明这次集合执行完全成功
                collection_principal_stats[principal_id]["success_count"] += 1
            else:
                # 有失败用例，说明这次集合执行有失败
                collection_principal_stats[principal_id]["failed_count"] += 1
        
        # 转换集合负责人数据并获取用户名
        collection_principal_distribution = []
        for principal_id, stats in collection_principal_stats.items():
            # 获取用户名
            user = User.query.filter_by(access_user_id=principal_id).first()
            principal_name = user.access_name if user else principal_id
            
            total_executions = stats["collection_count"]
            success_rate_coll = round(stats["success_count"] / total_executions * 100, 2) if total_executions > 0 else 0
            
            collection_principal_distribution.append({
                "principal_id": principal_id,
                "principal_name": principal_name,
                "collection_count": stats["collection_count"],
                "success_count": stats["success_count"],
                "failed_count": stats["failed_count"],
                "success_rate": success_rate_coll
            })
        
        # =========================
        # 3. 项目维度分布
        # =========================
        # 获取所有collection_info_id对应的项目信息
        collection_ids = [r.collection_info_id for r in history_records]
        collection_project_map = {}
        if collection_ids:
            collections = WebCollectionInfo.query.filter(
                WebCollectionInfo.id.in_(collection_ids)
            ).all()
            for coll in collections:
                collection_project_map[coll.id] = coll.project_id
        
        # 按项目统计
        project_stats = {}
        for record in history_records:
            project_id = collection_project_map.get(record.collection_info_id)
            if not project_id:
                continue
                
            if project_id not in project_stats:
                project_stats[project_id] = {
                    "project_id": project_id,
                    "execution_count": 0,  # 集合执行总数
                    "success_count": 0,    # 通过用例数
                    "failed_count": 0      # 失败用例数
                }
            
            # 集合执行次数累加
            project_stats[project_id]["execution_count"] += 1
            
            # 从 history_desc 提取通过数和失败数
            _, success_num, failed_num = parse_history_desc(record.history_desc)
            project_stats[project_id]["success_count"] += success_num
            project_stats[project_id]["failed_count"] += failed_num
        
        # 转换项目数据并获取项目名
        project_distribution = []
        for project_id, stats in project_stats.items():
            # 获取项目名
            project = WebProject.query.filter_by(id=project_id).first()
            project_name = project.project_name if project else f"项目{project_id}"
            
            total_cases = stats["success_count"] + stats["failed_count"]
            success_rate_proj = round(stats["success_count"] / total_cases * 100, 2) if total_cases > 0 else 0
            
            project_distribution.append({
                "project_id": project_id,
                "project_name": project_name,
                "execution_count": stats["execution_count"],
                "total_cases": total_cases,
                "success_count": stats["success_count"],
                "failed_count": stats["failed_count"],
                "success_rate": success_rate_proj
            })
        
        # =========================
        # 组装返回数据
        # =========================
        result_data = {
            "overview": overview_data,
            "distribution": {
                "case_principal": case_principal_distribution,
                "collection_principal": collection_principal_distribution,
                "project": project_distribution
            }
        }
        
        return respModel.ok_resp(msg="查询成功", dic_t=result_data)

    except Exception as e:
        print(f"质量大盘数据统计异常: {e}")
        import traceback
        traceback.print_exc()
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@module_route.route(f"/{module_name}/getQualityDetail", methods=["POST"])
def get_quality_Detail():
    """
    质量大盘明细数据接口
    返回基于WebHistoryTimeModel表的明细数据（不去重）
    """
    try:
        # 获取筛选参数
        params = request.json
        start_date = params.get("start_date")  # 格式：YYYY-MM-DD
        end_date = params.get("end_date")      # 格式：YYYY-MM-DD
        project_ids = params.get("project_ids", [])  # 项目ID列表
        collection_env_types = params.get("collection_env_type", [])  # 环境类型列表：common/test/stage/online
        
        # 构建基础查询过滤条件
        filter_list = []
        
        # 日期范围筛选
        if start_date:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            filter_list.append(WebHistoryTimeModel.create_time >= start_datetime)
        if end_date:
            end_datetime = datetime.strptime(end_date + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
            filter_list.append(WebHistoryTimeModel.create_time <= end_datetime)
        
        # 环境类型筛选
        if collection_env_types and len(collection_env_types) > 0:
            filter_list.append(WebHistoryTimeModel.collection_env_type.in_(collection_env_types))
        
        # 获取基础历史记录数据
        history_records = WebHistoryTimeModel.query.filter(*filter_list).all()
        print(f"[DEBUG Detail] 日期筛选后记录数: {len(history_records)}")
        
        # 项目筛选
        if project_ids and len(project_ids) > 0:
            # 获取符合项目条件的collection_info_id
            valid_collection_ids = [c.id for c in WebCollectionInfo.query.filter(
                WebCollectionInfo.project_id.in_(project_ids)
            ).all()]
            history_records = [r for r in history_records if r.collection_info_id in valid_collection_ids]
            print(f"[DEBUG Detail] 项目筛选后记录数: {len(history_records)}, 项目IDs: {project_ids}")
        
        # 解析history_desc判断是否通过
        def parse_history_desc(desc):
            """解析历史描述，返回(总数, 通过数, 失败数)"""
            if not desc:
                return 0, 0, 0
            try:
                import re
                total = re.search(r'总数[：:]\s*(\d+)', desc)
                success = re.search(r'通过\s*(\d+)', desc)
                failed = re.search(r'失败\s*(\d+)', desc)
                
                total_num = int(total.group(1)) if total else 0
                success_num = int(success.group(1)) if success else 0
                failed_num = int(failed.group(1)) if failed else 0
                
                return total_num, success_num, failed_num
            except Exception as e:
                print(f"解析history_desc失败: {desc}, 错误: {e}")
                return 0, 0, 0
        
        # 获取所有需要的集合信息（批量查询）
        collection_ids = list(set([r.collection_info_id for r in history_records]))
        collection_map = {}
        if collection_ids:
            collections = WebCollectionInfo.query.filter(
                WebCollectionInfo.id.in_(collection_ids)
            ).all()
            for coll in collections:
                collection_map[coll.id] = coll
        
        # 获取所有用例信息（用于查询用例详情）
        all_case_ids = set()
        for record in history_records:
            # 从 pass_cases_detail 提取 case_id
            if hasattr(record, 'pass_cases_detail') and record.pass_cases_detail:
                try:
                    pass_cases = json.loads(record.pass_cases_detail)
                    for case in pass_cases:
                        case_id = case.get("case_id")
                        # 尝试将 case_id 转换为整数（可能是字符串类型）
                        if case_id:
                            try:
                                if isinstance(case_id, str):
                                    case_id = int(case_id)
                                if isinstance(case_id, int):
                                    all_case_ids.add(case_id)
                            except (ValueError, TypeError):
                                pass
                except:
                    pass
            # 从 failed_cases_detail 提取 case_id
            if record.failed_cases_detail:
                try:
                    failed_cases = json.loads(record.failed_cases_detail)
                    for case in failed_cases:
                        case_id = case.get("case_id")
                        # 尝试将 case_id 转换为整数（可能是字符串类型）
                        if case_id:
                            try:
                                if isinstance(case_id, str):
                                    case_id = int(case_id)
                                if isinstance(case_id, int):
                                    all_case_ids.add(case_id)
                            except (ValueError, TypeError):
                                pass
                except:
                    pass
        
        # 批量查询用例信息
        case_info_map = {}
        if all_case_ids:
            case_infos = WebInfo.query.filter(WebInfo.id.in_(all_case_ids)).all()
            for case_info in case_infos:
                case_info_map[case_info.id] = case_info
        
        # 构建明细数据
        detail_list = []
        for record in history_records:
            # 获取集合信息
            collection = collection_map.get(record.collection_info_id)
            collection_name = collection.collection_name if collection else ""
            collection_desc = collection.collection_desc if collection else ""
            
            # 获取集合负责人信息
            collection_principal_id = record.collection_principal if record.collection_principal else "无"
            collection_principal_user = User.query.filter_by(access_user_id=collection_principal_id).first()
            collection_principal_name = collection_principal_user.access_name if collection_principal_user else collection_principal_id
            
            # 获取集合内用例信息
            cases_list = []
            
            # 处理通过的用例
            if hasattr(record, 'pass_cases_detail') and record.pass_cases_detail:
                try:
                    pass_cases = json.loads(record.pass_cases_detail)
                    for case in pass_cases:
                        case_id = case.get("case_id")
                        case_name = case.get("case_name", "")
                        case_principal_id = case.get("principal", "无")
                        
                        # 获取用例详情（将 case_id 转换为整数后查询）
                        case_desc = ""
                        try:
                            case_id_int = int(case_id) if isinstance(case_id, str) else case_id
                            if isinstance(case_id_int, int) and case_id_int in case_info_map:
                                case_info = case_info_map.get(case_id_int)
                                case_desc = case_info.case_desc if case_info else ""
                        except (ValueError, TypeError):
                            pass
                        
                        # 获取用例负责人名称
                        case_principal_user = User.query.filter_by(access_user_id=case_principal_id).first()
                        case_principal_name = case_principal_user.access_name if case_principal_user else case_principal_id
                        
                        cases_list.append({
                            "case_id": case_id if case_id else "未知",
                            "case_name": case_name,
                            "case_desc": case_desc,
                            "case_principal_id": case_principal_id,
                            "case_principal_name": case_principal_name,
                            "is_pass": True  # 记录在 pass_cases_detail 中为通过
                        })
                except Exception as e:
                    print(f"解析 pass_cases_detail 失败: {e}")
            
            # 处理失败的用例
            if record.failed_cases_detail:
                try:
                    failed_cases = json.loads(record.failed_cases_detail)
                    for case in failed_cases:
                        case_id = case.get("case_id")
                        case_name = case.get("case_name", "")
                        case_principal_id = case.get("principal", "无")
                        
                        # 获取用例详情（将 case_id 转换为整数后查询）
                        case_desc = ""
                        try:
                            case_id_int = int(case_id) if isinstance(case_id, str) else case_id
                            if isinstance(case_id_int, int) and case_id_int in case_info_map:
                                case_info = case_info_map.get(case_id_int)
                                case_desc = case_info.case_desc if case_info else ""
                        except (ValueError, TypeError):
                            pass
                        
                        # 获取用例负责人名称
                        case_principal_user = User.query.filter_by(access_user_id=case_principal_id).first()
                        case_principal_name = case_principal_user.access_name if case_principal_user else case_principal_id
                        
                        cases_list.append({
                            "case_id": case_id if case_id else "未知",
                            "case_name": case_name,
                            "case_desc": case_desc,
                            "case_principal_id": case_principal_id,
                            "case_principal_name": case_principal_name,
                            "is_pass": False  # 记录在 failed_cases_detail 中为失败
                        })
                except Exception as e:
                    print(f"解析 failed_cases_detail 失败: {e}")
            
            # 判断集合是否通过：基于实际用例的执行结果
            # 如果所有用例都通过（或没有用例），则集合通过
            is_pass = all(case.get("is_pass", False) for case in cases_list) if cases_list else True
            
            # 组装集合明细数据
            detail_list.append({
                "collection_id": record.collection_info_id,
                "collection_name": collection_name,
                "collection_desc": collection_desc,
                "collection_env_type": record.collection_env_type if hasattr(record, 'collection_env_type') else "common",
                "is_pass": is_pass,
                "collection_principal_id": collection_principal_id,
                "collection_principal_name": collection_principal_name,
                "execute_time": record.create_time.strftime('%Y-%m-%d %H:%M:%S') if record.create_time else "",
                "cases": cases_list
            })
        
        print(f"[DEBUG Detail] detail_list 构建完成，最终长度: {len(detail_list)}，history_records 总数: {len(history_records)}")
        return respModel.ok_resp(msg="查询成功", dic_t={"detail_list": detail_list, "total": len(detail_list)})

    except Exception as e:
        print(f"质量大盘明细查询异常: {e}")
        import traceback
        traceback.print_exc()
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@module_route.route(f"/{module_name}/getQualityAIData", methods=["POST"])
def get_quality_AI_data():
    """
    质量大盘AI分析接口
    基于单日明细数据，通过AI生成业务价值分析报告
    
    入参：
    - start_date: 开始日期（YYYY-MM-DD）
    - end_date: 结束日期（YYYY-MM-DD），必须与start_date相同（仅支持单日分析）
    - project_ids: 项目ID列表（可选），为空则查询所有项目
    - collection_env_type: 环境类型列表（可选），为空则查询所有环境
    """
    try:
        # 1. 获取并验证参数
        params = request.json
        start_date = params.get("start_date")  # 格式：YYYY-MM-DD
        end_date = params.get("end_date")      # 格式：YYYY-MM-DD
        
        if not start_date or not end_date:
            return respModel.error_resp("请提供 start_date 和 end_date 参数")
        
        # 验证日期跨度不超过1天
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            date_diff = (end_dt - start_dt).days
            
            if date_diff != 0:
                return respModel.error_resp("仅支持单日数据分析，start_date 和 end_date 必须为同一天")
        except ValueError as e:
            return respModel.error_resp(f"日期格式错误，请使用 YYYY-MM-DD 格式: {e}")
        
        # 2. 获取明细数据（复用 get_quality_Detail 的逻辑）
        project_ids = params.get("project_ids", [])
        collection_env_types = params.get("collection_env_type", [])  # 环境类型列表
        
        # 构建基础查询过滤条件
        filter_list = []
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        filter_list.append(WebHistoryTimeModel.create_time >= start_datetime)
        end_datetime = datetime.strptime(end_date + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
        filter_list.append(WebHistoryTimeModel.create_time <= end_datetime)
        
        # 环境类型筛选
        if collection_env_types and len(collection_env_types) > 0:
            filter_list.append(WebHistoryTimeModel.collection_env_type.in_(collection_env_types))
        
        # 获取基础历史记录数据
        history_records = WebHistoryTimeModel.query.filter(*filter_list).all()
        print(f"[DEBUG AI] 日期筛选后记录数: {len(history_records)}")
        
        # 项目筛选
        if project_ids and len(project_ids) > 0:
            valid_collection_ids = [c.id for c in WebCollectionInfo.query.filter(
                WebCollectionInfo.project_id.in_(project_ids)
            ).all()]
            history_records = [r for r in history_records if r.collection_info_id in valid_collection_ids]
            print(f"[DEBUG AI] 项目筛选后记录数: {len(history_records)}, 项目IDs: {project_ids}")
        
        if not history_records:
            return respModel.error_resp("该日期范围内没有执行记录，无法进行AI分析")
        
        # 解析 history_desc
        def parse_history_desc(desc):
            if not desc:
                return 0, 0, 0
            try:
                import re
                total = re.search(r'总数[：:]\s*(\d+)', desc)
                success = re.search(r'通过\s*(\d+)', desc)
                failed = re.search(r'失败\s*(\d+)', desc)
                return (int(total.group(1)) if total else 0,
                        int(success.group(1)) if success else 0,
                        int(failed.group(1)) if failed else 0)
            except:
                return 0, 0, 0
        
        # 获取所有需要的数据（集合、用例、项目、用户）
        collection_ids = list(set([r.collection_info_id for r in history_records]))
        collection_map = {}
        collection_project_map = {}
        if collection_ids:
            collections = WebCollectionInfo.query.filter(
                WebCollectionInfo.id.in_(collection_ids)
            ).all()
            for coll in collections:
                collection_map[coll.id] = coll
                collection_project_map[coll.id] = coll.project_id
        
        # 获取项目信息
        project_ids_set = set(collection_project_map.values())
        project_map = {}
        if project_ids_set:
            projects = WebProject.query.filter(WebProject.id.in_(list(project_ids_set))).all()
            for proj in projects:
                project_map[proj.id] = proj
        
        # 获取所有用例信息
        all_case_ids = set()
        for record in history_records:
            if hasattr(record, 'pass_cases_detail') and record.pass_cases_detail:
                try:
                    pass_cases = json.loads(record.pass_cases_detail)
                    for case in pass_cases:
                        case_id = case.get("case_id")
                        if case_id:
                            try:
                                if isinstance(case_id, str):
                                    case_id = int(case_id)
                                if isinstance(case_id, int):
                                    all_case_ids.add(case_id)
                            except (ValueError, TypeError):
                                pass
                except:
                    pass
            if record.failed_cases_detail:
                try:
                    failed_cases = json.loads(record.failed_cases_detail)
                    for case in failed_cases:
                        case_id = case.get("case_id")
                        if case_id:
                            try:
                                if isinstance(case_id, str):
                                    case_id = int(case_id)
                                if isinstance(case_id, int):
                                    all_case_ids.add(case_id)
                            except (ValueError, TypeError):
                                pass
                except:
                    pass
        
        # 批量查询用例信息
        case_info_map = {}
        if all_case_ids:
            case_infos = WebInfo.query.filter(WebInfo.id.in_(all_case_ids)).all()
            for case_info in case_infos:
                case_info_map[case_info.id] = case_info
        
        # 获取所有用户信息
        all_principal_ids = set()
        for record in history_records:
            if record.collection_principal:
                all_principal_ids.add(record.collection_principal)
        for case_info in case_info_map.values():
            if case_info.principal:
                all_principal_ids.add(case_info.principal)
        
        user_map = {}
        if all_principal_ids:
            users = User.query.filter(User.access_user_id.in_(list(all_principal_ids))).all()
            for user in users:
                user_map[user.access_user_id] = user.access_name
        
        # 3. 构建结构化数据用于AI分析（增强：只对失败的集合，从Allure报告按需提取失败详情）
        detail_list = []
        
        print(f"[DEBUG AI] 开始构建 detail_list，history_records 数量: {len(history_records)}")
        for idx, record in enumerate(history_records):
            collection = collection_map.get(record.collection_info_id)
            collection_name = collection.collection_name if collection else ""
            collection_desc = collection.collection_desc if collection else ""
            project_id = collection_project_map.get(record.collection_info_id)
            project = project_map.get(project_id)
            project_name = project.project_name if project else "未知项目"
            
            collection_principal_id = record.collection_principal if record.collection_principal else "无"
            collection_principal_name = user_map.get(collection_principal_id, collection_principal_id)
            
            _, _, failed_num = parse_history_desc(record.history_desc)
            
            # 获取用例详情
            cases_list = []
            
            # 通过的用例
            if hasattr(record, 'pass_cases_detail') and record.pass_cases_detail:
                try:
                    pass_cases = json.loads(record.pass_cases_detail)
                    for case in pass_cases:
                        case_id = case.get("case_id")
                        case_name = case.get("case_name", "")
                        case_principal_id = case.get("principal", "无")
                        
                        case_desc = ""
                        try:
                            case_id_int = int(case_id) if isinstance(case_id, str) else case_id
                            if isinstance(case_id_int, int) and case_id_int in case_info_map:
                                case_info = case_info_map.get(case_id_int)
                                case_desc = case_info.case_desc if case_info else ""
                        except (ValueError, TypeError):
                            pass
                        
                        case_principal_name = user_map.get(case_principal_id, case_principal_id)
                        
                        cases_list.append({
                            "case_name": case_name,
                            "case_desc": case_desc,
                            "case_principal_name": case_principal_name,
                            "is_pass": True
                        })
                except:
                    pass
            
            # 失败的用例（增强：按需从Allure报告提取失败详情）
            if record.failed_cases_detail:
                try:
                    failed_cases = json.loads(record.failed_cases_detail)
                    
                    # 只有当有失败用例时，才去读取Allure报告（按需加载）
                    allure_failure_map = {}
                    if failed_cases and record.history_detail:
                        allure_failure_map = extract_allure_failure_details(record.history_detail)
                    
                    for case in failed_cases:
                        case_id = case.get("case_id")
                        case_name = case.get("case_name", "")
                        case_principal_id = case.get("principal", "无")
                        
                        case_desc = ""
                        try:
                            case_id_int = int(case_id) if isinstance(case_id, str) else case_id
                            if isinstance(case_id_int, int) and case_id_int in case_info_map:
                                case_info = case_info_map.get(case_id_int)
                                case_desc = case_info.case_desc if case_info else ""
                        except (ValueError, TypeError):
                            pass
                        
                        case_principal_name = user_map.get(case_principal_id, case_principal_id)
                        
                        # 构建基础用例信息
                        case_data = {
                            "case_name": case_name,
                            "case_desc": case_desc,
                            "case_principal_name": case_principal_name,
                            "is_pass": False
                        }
                        
                        # 如果从Allure中提取到了失败详情，添加进去
                        if case_name in allure_failure_map:
                            case_data["failure_details"] = allure_failure_map[case_name]
                        
                        cases_list.append(case_data)
                except:
                    pass
            
            is_pass = all(case.get("is_pass", False) for case in cases_list) if cases_list else True
            
            detail_list.append({
                "project_name": project_name,
                "collection_name": collection_name,
                "collection_desc": collection_desc,
                "collection_env_type": record.collection_env_type if hasattr(record, 'collection_env_type') else "common",
                "is_pass": is_pass,
                "collection_principal_name": collection_principal_name,
                "execute_time": record.create_time.strftime('%Y-%m-%d %H:%M:%S') if record.create_time else "",
                "cases": cases_list
            })
            
            if (idx + 1) % 10 == 0:
                print(f"[DEBUG AI] 已处理 {idx + 1}/{len(history_records)} 条记录，当前 detail_list 长度: {len(detail_list)}")
        
        print(f"[DEBUG AI] detail_list 构建完成，最终长度: {len(detail_list)}，history_records 总数: {len(history_records)}")
        
        # 4. 构建AI分析的Prompt（基于实际数据能力）
        data_json = json.dumps(detail_list, ensure_ascii=False, indent=2)
        
        # 预先统计真实数据（避免AI统计不准确）
        total_collections = len(detail_list)
        passed_collections = sum(1 for d in detail_list if d.get("is_pass", False))
        failed_collections = total_collections - passed_collections
        collection_pass_rate = round(passed_collections / total_collections * 100, 1) if total_collections > 0 else 0
        
        total_cases = sum(len(d.get("cases", [])) for d in detail_list)
        passed_cases = sum(1 for d in detail_list for case in d.get("cases", []) if case.get("is_pass", False))
        failed_cases = total_cases - passed_cases
        case_pass_rate = round(passed_cases / total_cases * 100, 1) if total_cases > 0 else 0
        
        # 统计涉及的项目
        projects = list(set([d.get("project_name", "未知项目") for d in detail_list]))
        
        # 统计负责人
        principals = list(set([d.get("collection_principal_name", "无") for d in detail_list]))
        
        print(f"[AI分析统计] 执行记录: {total_collections}条, 通过: {passed_collections}条, 失败: {failed_collections}条, 集合通过率: {collection_pass_rate}%")
        print(f"[AI分析统计] 用例总数: {total_cases}个, 通过: {passed_cases}个, 失败: {failed_cases}个, 用例通过率: {case_pass_rate}%")
        print(f"[AI分析统计] 涉及项目: {', '.join(projects)}")
        
        prompt = f"""你是一位专业的测试质量分析专家，请基于以下 Web 自动化测试执行数据，生成一份有业务价值的质量分析报告。

【重要说明】
本次数据为 {len(detail_list)} 条执行记录，代表当天的所有集合执行情况。
- 数据来源：定时任务的自动化执行记录（可能包含同一集合的多次执行）
- 统计规则：每条记录独立统计，不去重

【执行数据】
{data_json}

【数据字段说明】
- project_name: 所属项目
- collection_name: 测试集合名称（同一集合可能在一天内执行多次，每次独立统计）
- collection_desc: 测试集合的业务描述（这是理解业务价值的关键）
- collection_env_type: 测试环境类型（common=通用环境，test=测试环境，stage=预发布环境，online=生产环境）
  **注意**：如果值为 "common"，代表该集合同时覆盖多个环境，此时可参考 collection_name 或 collection_desc 中的环境信息进行判断
- is_pass: 该集合所有用例是否全部通过
- collection_principal_name: 集合负责人
- execute_time: 执行时间
- cases: 该集合包含的用例列表
  - case_name: 用例名称（通常包含业务功能点）
  - case_desc: 用例的详细业务描述（包含操作步骤、验证点等，是理解业务场景的核心）
  - case_principal_name: 用例负责人
  - is_pass: 该用例是否通过
  - failure_details: 失败详情（仅失败用例有此字段）
    - error_type: 错误类型（AssertionError/TimeoutException/NoSuchElementException等）
    - error_message: 完整错误信息（包含元素定位符、超时时间、断言预期值等关键信息）
    - error_trace_summary: 错误堆栈摘要（实际出错位置）
    - failed_step_name: 失败的具体步骤名称
    - failed_step_index: 第几步失败（从1开始）
    - total_steps: 总步骤数

【基础数据统计】（请直接使用以下统计结果）
- 执行记录总数：{total_collections} 条
- 通过的执行记录：{passed_collections} 条
- 失败的执行记录：{failed_collections} 条
- 集合执行通过率：{collection_pass_rate}%
- 测试用例总数：{total_cases} 个
- 通过的用例数：{passed_cases} 个
- 失败的用例数：{failed_cases} 个
- 用例通过率：{case_pass_rate}%
- 涉及项目：{', '.join(projects)}
- 主要负责人：{', '.join(principals)}

【分析要求】

## 一、执行概况（直接使用上面的基础数据统计）
- 直接引用【基础数据统计】中的数据，不要重新统计
- 简洁呈现即可，重点在第二、三部分

## 二、业务功能分析（核心部分，必须重点利用desc字段）

**说明**：数据中共有 {total_collections} 条执行记录，包含 {failed_collections} 条失败记录。同一个集合可能在一天内执行多次，请将相同集合名称的执行记录合并分析。

1. **功能模块识别**：
   - 从 collection_name、collection_desc、case_name、case_desc 中提取业务功能点
   - 将相似功能归类为业务模块（如：用户管理、资源管理、班级管理等）
   - 每个模块列出包含的主要功能和执行情况（去重统计不同的集合/用例）

2. **失败功能深度分析**（质量大盘的核心价值）：
   - 列出所有失败的执行记录（共 {failed_collections} 条）
   - 对于相同集合名称的失败，合并分析（说明执行了几次、失败几次）
   - **环境维度分析**（可选）：
     * 如果需要，可以按 collection_env_type 字段进行环境分类统计（test/stage/online/common）
     * 如果失败集合的 collection_env_type 为 "common"，可以从 collection_name 或 collection_desc 中提取具体环境信息
     * 分析不同环境的失败分布，识别是否存在环境特异性问题（例如：仅测试环境失败，生产环境正常）
   - **重点解读 case_desc**，说明这些失败的用例具体测试了什么业务操作
   - **充分利用 failure_details**（如果有）：
     * 从 error_type 识别问题类型（断言失败、元素找不到、超时等）
     * 从 error_message 提取关键信息（如哪个元素找不到、哪个断言失败）
     * 从 failed_step_name 和 failed_step_index 精准定位失败位置（如："第X步失败：步骤名称"）
     * 结合 error_trace_summary 分析技术层面的失败原因
   - 分析失败对业务的影响（用户体验、核心流程、数据准确性等）
   - **给出具体的失败原因推断**：
     * 如果是 NoSuchElementException：可能是页面改版、元素定位过时
     * 如果是 TimeoutException：可能是网络慢、页面加载慢、性能问题
     * 如果是 AssertionError：可能是功能缺陷、数据异常、环境配置错误
   - 用清晰的结构呈现（建议用表格或分点列表）

3. **通过功能概览**：
   - 汇总正常运行的核心业务功能（去重统计不同的集合）
   - 体现测试的业务价值（证明哪些功能稳定可用）

## 三、改进建议（可落地的行动项）
1. **失败问题修复方向**（基于 failure_details 给出精准建议）：
   - **元素定位问题**（NoSuchElementException）：
     * **推荐方案**：采用 AI 视觉识别技术替代传统元素定位方式，通过图像识别或文本识别来定位页面元素，从根本上解决元素定位符过时、页面改版导致的定位失败问题
     * 备选方案：如果暂时无法使用 AI 视觉方式，可以检查页面是否改版，更新元素定位符为更稳定的定位方式（如data-testid）
   - **超时问题**（TimeoutException）：
     * **推荐方案**：采用 AI 视觉识别技术，基于页面实际呈现进行交互，避免因等待时间设置不当导致的超时问题；AI 视觉方式可以智能识别页面加载完成状态
     * 备选方案：分析页面性能问题，适当增加等待时间；检查网络环境，优化测试环境配置
   - **断言失败**（AssertionError）：
     * 基于 error_message 分析预期值和实际值差异
     * 判断是功能缺陷还是测试数据问题
     * 如果是环境配置问题（如URL配置错误），给出具体配置建议
   - 针对每个失败功能，结合 case_desc 和 failure_details 给出具体修复建议

2. **质量提升建议**：
   - 从测试稳定性角度：针对高频失败的错误类型（如超时、元素找不到）优化用例设计
   - 从测试执行角度：失败用例的处理机制、回归测试策略
   - 从用例维护角度：定期检查元素定位符、更新过时的测试数据
   - 从团队协作角度：负责人响应机制、问题跟踪流程

【特别注意】
1. **desc字段是核心**：collection_desc 和 case_desc 包含了业务价值信息，不要只看名称，要深入解读描述内容
2. **failure_details是分析利器**：如果失败用例有 failure_details，必须充分利用：
   - error_type 告诉你问题类型（断言/超时/元素找不到/语法错误等）
   - error_message 包含关键细节（如哪个元素、哪个断言、预期值是什么）
   - failed_step_name 精准定位哪一步失败
   - 结合这些信息，可以给出远超"功能失败"的深度分析
3. **避免空泛描述**：不要只说"功能失败"，要说清楚"哪个具体业务操作的第几步失败了，错误类型是什么，影响什么"
4. **分析维度灵活**：按实际数据特点分析，可以按项目、业务模块、负责人、错误类型等维度，不要强加不存在的分类
5. **不涉及覆盖率**：数据中没有覆盖率信息，不要分析覆盖率
6. **突出业务价值**：这不是纯技术报告，要让业务人员也能看懂失败影响了什么，同时给开发/测试人员提供可操作的修复方向

【输出格式】
使用 Markdown 格式，结构清晰，重点突出，避免冗长。

请生成质量分析报告："""
        
        # 5. 调用AI模型
        cfg = get_runtime_ai_settings()
        os.environ["OPENAI_API_KEY"] = cfg["api_key"]

        print(f"[AI分析] 开始调用豆包模型，数据日期: {start_date}, 记录数: {len(detail_list)}, 失败记录: {failed_collections}条, 失败用例: {failed_cases}个")

        response = requests.post(
            f"{cfg['api_base']}/chat/completions",
            headers={
                "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
                "Content-Type": "application/json"
            },
            json={
                "model": cfg["text_model"],
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "text": prompt,
                                "type": "text"
                            }
                        ]
                    }
                ],
                "thinking": {
                    "type": "disabled"
                }
            },
            timeout=120  # 设置60秒超时
        )
        
        if response.status_code != 200:
            print(f"[AI分析] API调用失败: {response.status_code}, {response.text}")
            return respModel.error_resp(f"AI模型调用失败: {response.status_code}")
        
        try:
            ai_result = response.json()
            print(f"[AI分析] 模型返回: {ai_result}")
            ai_analysis = ai_result["choices"][0]["message"]["content"].strip()
            
            return respModel.ok_resp(
                msg="AI分析成功",
                dic_t={
                    "analysis_date": start_date,
                    "total_collections": len(detail_list),
                    "ai_analysis": ai_analysis,
                    "raw_data_summary": {
                        "total_collections": len(detail_list),
                        "total_cases": sum(len(d["cases"]) for d in detail_list),
                        "projects": list(set(d["project_name"] for d in detail_list))
                    }
                }
            )
        except Exception as e:
            print(f"[AI分析] 解析响应失败: {e}")
            return respModel.error_resp(f"AI响应解析失败: {e}")

    except Exception as e:
        print(f"质量大盘AI分析异常: {e}")
        import traceback
        traceback.print_exc()
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")