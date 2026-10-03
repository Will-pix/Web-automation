# import ast
#
# def safe_parse(invalid_str: str):
#     """处理字典/JSON格式微修正，返回解析结果或None"""
#     # 替换JSON关键字
#     s = invalid_str.replace("true", "True").replace("false", "False").replace("null", "None")
#     try:
#         return ast.literal_eval(s)
#     except (SyntaxError, ValueError) as e:
#         print(f"输入「{invalid_str}」解析失败：{e.__class__.__name__} - {e}")
#         return None
#
# # ==================== 场景1：属于Python字面量（能正常解析） ====================
# print("===== 能正常解析的非字典/JSON格式 =====")
# # 1. 纯字符串（带引号，是Python字面量）
# print(safe_parse('"hello world"'))  # 输出：hello world
# # 2. 纯数字（整数/浮点数）
# print(safe_parse('123'))            # 输出：123
# print(safe_parse('3.14159'))        # 输出：3.14159
# # 3. 布尔值/None（JSON的true/null替换后）
# print(safe_parse('true'))           # 输出：True（替换后是Python的True）
# print(safe_parse('null'))           # 输出：None（替换后是Python的None）
# # 4. 元组（Python字面量，JSON不支持）
# print(safe_parse('(1, 2, 3,)'))     # 输出：(1, 2, 3)（多余逗号也能处理）
# print()
#
# # ==================== 场景2：不属于Python字面量（解析失败，返回None） ====================
# print("===== 解析失败的非字典/JSON格式 =====")
# # 1. 无引号的普通文本（不是Python字面量，语法错误）
# print(safe_parse('hello world'))    # 解析失败，返回None
# # 2. 表达式（ast.literal_eval不支持计算/表达式）
# print(safe_parse('1 + 2'))          # 解析失败，返回None
# print(safe_parse('"a" + "b"'))      # 解析失败，返回None
# # 3. 函数调用（非字面量）
# print(safe_parse('len("abc")'))     # 解析失败，返回None
# # 4. 注释（非字面量，语法错误）
# print(safe_parse('123 # 这是注释')) # 解析失败，返回None
# # 5. 完全无意义的字符（语法错误）
# print(safe_parse('@#$%^&*'))        # 解析失败，返回None
# # 6. 混合有效和无效内容（语法错误）
# print(safe_parse('{"name": "张三"} + {"age": 20}'))  # 解析失败，返回None