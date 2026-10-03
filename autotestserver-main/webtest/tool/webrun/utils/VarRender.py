# 字符串模板进行参数渲染
# 使用 jinjia2 模板引擎 (类似 flask的模板)
# https://docs.jinkan.org/docs/jinja2/templates.html
from jinja2 import Template, UndefinedError


def refresh(target, context):
    if target is None: return None
    return Template(str(target)).render(context)

# def refresh(target, context):
#     if target is None:
#         return None
#
#     # 处理字符串：使用 Jinja2 模板替换 {{变量}}
#     if isinstance(target, str):
#         try:
#             # 用 Jinja2 渲染，支持 {{变量}} 格式
#             return Template(target).render(context)
#         except UndefinedError:
#             # 若变量未定义，保留原占位符（模拟 safe_substitute 效果）
#             return target
#
#     # 处理字典/列表：递归替换
#     elif isinstance(target, dict):
#         return {k: refresh(v, context) for k, v in target.items()}
#     elif isinstance(target, list):
#         return [refresh(item, context) for item in target]
#     else:
#         return target

def test_refresh():
    # 单元测试用例 - 检查refresh是否有效
    target = "hello {{name}}, {{niasd}}"
    context = {"name": "张三"}
    result = refresh(target, context)
    print(result)

