# 飞书
import json

import requests


import requests
import json
from datetime import datetime

from sysmanage.model.user import User
from webtest.model.WebInfoModel import WebInfo
from webtest.model.WebCollectionInfoModel import WebCollectionInfo

from extensions import database
from flask import current_app
# from app import application

# 先定义环境类型映射字典（对应前端的映射表）
ENV_TYPE_MAPPING = {
    'common': '通用环境',
    'test': '测试环境',
    'stage': '预发布环境',
    'online': '生产环境'
}

# 调试执行
def webinfo_feishu(state,color,project, webcase, case_id, run_type, run_num, run_pass, run_fail, run_rate, run_time, report_url,principal):
    webhook_url = find_case_project(case_id)
    state = state
    # webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/05b755f3-a3b4-41a3-9549-d8d1283dd33e"
    project = project
    webcase = webcase
    case_id = case_id
    run_type = run_type
    run_num = run_num
    run_pass = run_pass
    run_fail = run_fail
    run_rate = run_rate
    run_time = run_time
    report_url = report_url
    color = color
    principal = principal
    print("principal", principal)
    principal_info = f"负责人：<at id=\"{principal}\"></at>" if principal else "负责人：无"
    values = [f"执行类型：{run_type}",f"用例名称：{webcase}", f"用例id：{case_id}", f"测试用例总数: {run_num}", f"通过数量: {run_pass}", f"失败数量: {run_fail}",
              f"通过率: {run_rate}", f"执行时长: {run_time}",principal_info]

    # 生成当前时间戳
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 构建消息体
    headers = {"Content-Type": "application/json"}
    body = {
        "msg_type": "interactive",
        "card": {
            "schema": "2.0",
            "config": {
                "update_multi": True,
                "style": {
                    "text_size": {
                        "normal_v2": {
                            "default": "normal",
                            "pc": "normal",
                            "mobile": "heading"
                        }
                    }
                }
            },
            "body": {
                "direction": "vertical",
                "padding": "12px 12px 12px 12px",
                "elements": [
                    {
                        "tag": "markdown",
                        "content": "\n".join(values),
                        "text_align": "left",
                        "text_size": "normal_v2",
                        "margin": "0px 0px 0px 0px"
                    },
                    {
                        "tag": "button",
                        "text": {
                            "tag": "plain_text",
                            "content": "📊点击查看详细报告"
                        },
                        "type": "primary",
                        "width": "default",
                        "size": "medium",
                        "behaviors": [
                            {
                                "type": "open_url",
                                "default_url": report_url,
                                "pc_url": "",
                                "ios_url": "",
                                "android_url": ""
                            }
                        ],
                        "margin": "0px 0px 0px 0px"
                    }
                ]
            },
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": f"{project}-Web自动化测试报告({timestamp})-{state}"
                },
                "subtitle": {
                    "tag": "plain_text",
                    "content": ""
                },
                "template": f"{color}",
                "padding": "12px 12px 12px 12px"
            }
        }
    }

    try:
        # 发送 POST 请求
        response = requests.post(webhook_url, headers=headers, data=json.dumps(body))

        # 检查响应状态
        if response.status_code == 200:
            print("消息发送成功！")
            print("响应内容:", response.json())
        else:
            print(f"消息发送失败，状态码: {response.status_code}")
            print("错误信息:", response.text)
        pass
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")
    except json.JSONDecodeError:
        print("无法解析响应内容，非 JSON 格式")
    except Exception as e:
        print(f"发生未知错误: {e}")

# 集合执行
def collection_feishu(collection_env_type,state,color,project, collection, collection_id, run_type, run_num, run_pass, run_fail, run_rate, run_time, report_url,principal,failed_cases=[]):
    webhook_url = find_suite_project(collection_id)
    state = state
    # webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/05b755f3-a3b4-41a3-9549-d8d1283dd33e"
    project = project
    collection = collection
    collection_id = collection_id
    run_type = run_type
    run_num = run_num
    run_pass = run_pass
    run_fail = run_fail
    run_rate = run_rate
    run_time = run_time
    report_url = report_url
    color = color
    principal = principal
    principal_info = f"集合负责人：<at id=\"{principal}\"></at>" if principal else "集合负责人：无"

    env_type_cn = ENV_TYPE_MAPPING.get(collection_env_type, "未知环境")


    values = [f"执行类型：{run_type}",f"执行环境：{env_type_cn}", f"集合名称：{collection}", f"集合id：{collection_id}", f"集合内用例总数: {run_num}", f"通过数量: {run_pass}", f"失败数量: {run_fail}",
              f"通过率: {run_rate}", f"执行时长: {run_time}", principal_info]

    # 生成当前时间戳
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ========== 新增：构建失败用例的markdown内容 ==========
    failed_content = ""
    if failed_cases:  # 有失败用例时才构建内容
        failed_content += "**集合内失败用例**\n"  # 标题
        for idx, case in enumerate(failed_cases, 1):
            # 处理用例负责人的@人：如果有principal（用户ID）则@人，否则显示“无”
            case_principal_at = f"<at id=\"{case['principal']}\"></at>" if case.get('principal') and case['principal'] != "无" else "无"
            # 拼接当前失败用例的信息（用例名、ID、负责人）
            # 如果有error_msg，可添加：f"错误信息：{case.get('error_msg', '无')[:200]}..."（截断避免过长）
            case_line = f"{idx}. 用例名：{case['case_name']} | 用例ID：{case['case_id']} | 用例负责人：{case_principal_at}\n"
            failed_content += case_line
    # =====================================================

    # 构建消息体
    headers = {"Content-Type": "application/json"}
    # body = {
    #     "msg_type": "interactive",
    #     "card": {
    #         "schema": "2.0",
    #         "config": {
    #             "update_multi": True,
    #             "style": {
    #                 "text_size": {
    #                     "normal_v2": {
    #                         "default": "normal",
    #                         "pc": "normal",
    #                         "mobile": "heading"
    #                     }
    #                 }
    #             }
    #         },
    #         "body": {
    #             "direction": "vertical",
    #             "padding": "12px 12px 12px 12px",
    #             "elements": [
    #                 {
    #                     "tag": "markdown",
    #                     "content": "\n".join(values),
    #                     "text_align": "left",
    #                     "text_size": "normal_v2",
    #                     "margin": "0px 0px 0px 0px"
    #                 },
    #                 {
    #                     "tag": "button",
    #                     "text": {
    #                         "tag": "plain_text",
    #                         "content": "📊点击查看详细报告"
    #                     },
    #                     "type": "primary",
    #                     "width": "default",
    #                     "size": "medium",
    #                     "behaviors": [
    #                         {
    #                             "type": "open_url",
    #                             "default_url": report_url,
    #                             "pc_url": "",
    #                             "ios_url": "",
    #                             "android_url": ""
    #                         }
    #                     ],
    #                     "margin": "0px 0px 0px 0px"
    #                 }
    #             ]
    #         },
    #         "header": {
    #             "title": {
    #                 "tag": "plain_text",
    #                 "content": f"{project}-Web自动化测试报告({timestamp})-{state}"
    #             },
    #             "subtitle": {
    #                 "tag": "plain_text",
    #                 "content": ""
    #             },
    #             "template": f"{color}",
    #             "padding": "12px 12px 12px 12px"
    #         }
    #     }
    # }

    body_elements = [
        {
            "tag": "markdown",
            "content": "\n".join(values),
            "text_align": "left",
            "text_size": "normal_v2",
            "margin": "0px 0px 0px 0px"
        }
    ]

    # ========== 新增：如果有失败用例，添加失败详情的markdown元素 ==========
    if failed_content:
        body_elements.append({
            "tag": "markdown",
            "content": failed_content,
            "text_align": "left",
            "text_size": "normal_v2",
            "margin": "0px 0px 0px 0px"  # 增加上边距，和上一个元素分隔开
        })
    # =====================================================

    # 添加按钮元素（放在最后）
    body_elements.append({
        "tag": "button",
        "text": {
            "tag": "plain_text",
            "content": "📊点击查看详细报告"
        },
        "type": "primary",
        "width": "default",
        "size": "medium",
        "behaviors": [
            {
                "type": "open_url",
                "default_url": report_url,
                "pc_url": "",
                "ios_url": "",
                "android_url": ""
            }
        ],
        "margin": "0px 0px 0px 0px"  # 增加上边距
    })

    body = {
        "msg_type": "interactive",
        "card": {
            "schema": "2.0",
            "config": {
                "update_multi": True,
                "style": {
                    "text_size": {
                        "normal_v2": {
                            "default": "normal",
                            "pc": "normal",
                            "mobile": "heading"
                        }
                    }
                }
            },
            "body": {
                "direction": "vertical",
                "padding": "12px 12px 12px 12px",
                "elements": body_elements  # 使用组装后的元素列表
            },
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": f"{project}-Web自动化测试报告({timestamp})-{state}"
                },
                "subtitle": {
                    "tag": "plain_text",
                    "content": ""
                },
                "template": f"{color}",
                "padding": "12px 12px 12px 12px"
            }
        }
    }

    try:
        # 发送 POST 请求
        response = requests.post(webhook_url, headers=headers, data=json.dumps(body))

        # 检查响应状态
        if response.status_code == 200:
            print("消息发送成功！")
            print("响应内容:", response.json())
        else:
            print(f"消息发送失败，状态码: {response.status_code}")
            print("错误信息:", response.text)
        pass
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")
    except json.JSONDecodeError:
        print("无法解析响应内容，非 JSON 格式")
    except Exception as e:
        print(f"发生未知错误: {e}")

# 集合执行-定时任务指定调用
def collection_feishu_time(collection_env_type,state,color,project, collection, collection_id, run_type, run_num, run_pass, run_fail, run_rate, run_time, report_url,principal,inform_value,failed_cases=[]):
    webhook_url = find_suite_project(collection_id)
    state = state
    # webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/05b755f3-a3b4-41a3-9549-d8d1283dd33e"
    project = project
    collection = collection
    collection_id = collection_id
    run_type = run_type
    run_num = run_num
    run_pass = run_pass
    run_fail = run_fail
    run_rate = run_rate
    run_time = run_time
    report_url = report_url
    color = color
    principal = principal
    inform_value = inform_value

    env_type_cn = ENV_TYPE_MAPPING.get(collection_env_type, "未知环境")

    if inform_value and state=="通过":
        # 这里需要将id转为name
        principal_name = get_user_name(principal)
        principal_info = f"集合负责人：{principal_name}" if principal_name else "集合负责人：无"
    else:
        principal_info = f"集合负责人：<at id=\"{principal}\"></at>" if principal else "集合负责人：无"

    values = [f"执行类型：{run_type}", f"执行环境：{env_type_cn}", f"集合名称：{collection}", f"集合id：{collection_id}", f"集合内用例总数: {run_num}", f"通过数量: {run_pass}", f"失败数量: {run_fail}",
              f"通过率: {run_rate}", f"执行时长: {run_time}", principal_info]

    # 生成当前时间戳
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ========== 新增：构建失败用例的markdown内容 ==========
    failed_content = ""
    if failed_cases:  # 有失败用例时才构建内容
        failed_content += "**集合内失败用例**\n"  # 标题
        for idx, case in enumerate(failed_cases, 1):
            # 处理用例负责人的@人：如果有principal（用户ID）则@人，否则显示“无”
            case_principal_at = f"<at id=\"{case['principal']}\"></at>" if case.get('principal') and case[
                'principal'] != "无" else "无"
            # 拼接当前失败用例的信息（用例名、ID、负责人）
            # 如果有error_msg，可添加：f"错误信息：{case.get('error_msg', '无')[:200]}..."（截断避免过长）
            case_line = f"{idx}. 用例名：{case['case_name']} | 用例ID：{case['case_id']} | 用例负责人：{case_principal_at}\n"
            failed_content += case_line
    # =====================================================

    # 构建消息体
    headers = {"Content-Type": "application/json"}
    # body = {
    #     "msg_type": "interactive",
    #     "card": {
    #         "schema": "2.0",
    #         "config": {
    #             "update_multi": True,
    #             "style": {
    #                 "text_size": {
    #                     "normal_v2": {
    #                         "default": "normal",
    #                         "pc": "normal",
    #                         "mobile": "heading"
    #                     }
    #                 }
    #             }
    #         },
    #         "body": {
    #             "direction": "vertical",
    #             "padding": "12px 12px 12px 12px",
    #             "elements": [
    #                 {
    #                     "tag": "markdown",
    #                     "content": "\n".join(values),
    #                     "text_align": "left",
    #                     "text_size": "normal_v2",
    #                     "margin": "0px 0px 0px 0px"
    #                 },
    #                 {
    #                     "tag": "button",
    #                     "text": {
    #                         "tag": "plain_text",
    #                         "content": "📊点击查看详细报告"
    #                     },
    #                     "type": "primary",
    #                     "width": "default",
    #                     "size": "medium",
    #                     "behaviors": [
    #                         {
    #                             "type": "open_url",
    #                             "default_url": report_url,
    #                             "pc_url": "",
    #                             "ios_url": "",
    #                             "android_url": ""
    #                         }
    #                     ],
    #                     "margin": "0px 0px 0px 0px"
    #                 }
    #             ]
    #         },
    #         "header": {
    #             "title": {
    #                 "tag": "plain_text",
    #                 "content": f"{project}-Web自动化测试报告({timestamp})-{state}"
    #             },
    #             "subtitle": {
    #                 "tag": "plain_text",
    #                 "content": ""
    #             },
    #             "template": f"{color}",
    #             "padding": "12px 12px 12px 12px"
    #         }
    #     }
    # }

    body_elements = [
        {
            "tag": "markdown",
            "content": "\n".join(values),
            "text_align": "left",
            "text_size": "normal_v2",
            "margin": "0px 0px 0px 0px"
        }
    ]

    # ========== 新增：如果有失败用例，添加失败详情的markdown元素 ==========
    if failed_content:
        body_elements.append({
            "tag": "markdown",
            "content": failed_content,
            "text_align": "left",
            "text_size": "normal_v2",
            "margin": "0px 0px 0px 0px"  # 增加上边距，和上一个元素分隔开
        })
    # =====================================================

    # 添加按钮元素（放在最后）
    body_elements.append({
        "tag": "button",
        "text": {
            "tag": "plain_text",
            "content": "📊点击查看详细报告"
        },
        "type": "primary",
        "width": "default",
        "size": "medium",
        "behaviors": [
            {
                "type": "open_url",
                "default_url": report_url,
                "pc_url": "",
                "ios_url": "",
                "android_url": ""
            }
        ],
        "margin": "0px 0px 0px 0px"  # 增加上边距
    })

    body = {
        "msg_type": "interactive",
        "card": {
            "schema": "2.0",
            "config": {
                "update_multi": True,
                "style": {
                    "text_size": {
                        "normal_v2": {
                            "default": "normal",
                            "pc": "normal",
                            "mobile": "heading"
                        }
                    }
                }
            },
            "body": {
                "direction": "vertical",
                "padding": "12px 12px 12px 12px",
                "elements": body_elements  # 使用组装后的元素列表
            },
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": f"{project}-Web自动化测试报告({timestamp})-{state}"
                },
                "subtitle": {
                    "tag": "plain_text",
                    "content": ""
                },
                "template": f"{color}",
                "padding": "12px 12px 12px 12px"
            }
        }
    }

    try:
        # 发送 POST 请求
        response = requests.post(webhook_url, headers=headers, data=json.dumps(body))

        # 检查响应状态
        if response.status_code == 200:
            print("消息发送成功！")
            print("响应内容:", response.json())
        else:
            print(f"消息发送失败，状态码: {response.status_code}")
            print("错误信息:", response.text)
        pass
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")
    except json.JSONDecodeError:
        print("无法解析响应内容，非 JSON 格式")
    except Exception as e:
        print(f"发生未知错误: {e}")

# 查询case所属部门
def find_case_project(case_id):
    try:
        # 手动创建应用上下文，确保数据库查询能正常执行
        from app import application
        with application.app_context():
            value = WebInfo.query.filter_by(id=case_id).first()
            if value:
                project_id = value.project_id
                print(f"对应的project_id是：{project_id}")
                weburl = find_project_webhookurl(project_id)
                return weburl
            else:
                print(f"未找到id为{case_id}的WebInfo记录")
                return None
    except Exception as e:
        print(f"查询失败：{e}")
        return None

# 查询集合所属部门
def find_suite_project(collection_id):
    try:
        # 手动创建应用上下文，确保数据库查询能正常执行
        from app import application
        with application.app_context():
            value = WebCollectionInfo.query.filter_by(id=collection_id).first()
            if value:
                project_id = value.project_id
                print(f"对应的project_id是：{project_id}")
                weburl = find_project_webhookurl(project_id)
                return weburl
            else:
                print(f"未找到id为{collection_id}的Wcollection_id记录")
                return None
    except Exception as e:
        print(f"查询失败：{e}")
        return None


# 根据部门查询所属webhook_url
def find_project_webhookurl(prokectid):
    # 优先从平台设置读取（前端管理的 Webhook URL）
    try:
        from platformconfig.service.runtime_store import load_settings
        settings = load_settings()
        notification = settings.get("notification", {})
        if notification.get("enabled", False):
            url = notification.get("webhook_url", "")
            if url:
                return url
    except Exception:
        pass
    # 回退到环境变量 / Flask config
    return current_app.config.get('FEISHU_WEBHOOK_URL') or ""

# 简化的ID转名称逻辑（假设用户数据一定存在）
def get_user_name(access_user_id):
    # 直接查询并返回名称（因确定有数据，无需异常处理和空值判断）
    return User.query.filter_by(access_user_id=access_user_id).first().access_name