# 模板代码
""""
返回值模板
"""
import  json

# class respModel():
#     # 用于生成包含单个对象数据的成功响应。
#     @staticmethod
#     def ok_resp(obj=None,msg=None,dic_t=None):
#         rsp={}
#         rsp["code"] = 200
#         rsp["msg"] = msg
#         data={}
#         if obj:
#             data = respModel().get_custom_attributes(obj)
#         if dic_t:
#             data.update(dic_t)
#         rsp["data"] = data
#         return rsp
#
#     # 用于生成包含对象列表数据的成功响应，同时包含数据总数。
#     @staticmethod
#     def ok_resp_list(obj=None,msg=None,lst=None,total=0):
#         rsp = {}
#         rsp["code"] = 200
#         rsp["msg"] = msg
#         rsp["total"] = total
#         lst1 =[]
#         if lst:
#             for obj in lst:
#                 dic = respModel().get_custom_attributes(obj)
#                 lst1.append(dic)
#         rsp["data"] = lst1
#         return rsp
#
#     # 生成一个简单的成功响应，直接将传入的列表数据作为响应数据。
#     @staticmethod
#     def ok_resp_simple(lst=None,msg=None):
#         rsp = {}
#         rsp["code"] = 200
#         rsp["msg"] = msg
#         rsp["data"] = lst
#         return rsp
#
#     # 生成一个简单的包含对象列表和总数的成功响应。
#     @staticmethod
#     def ok_resp_simple_list(lst=None, msg=None,total=0):
#         rsp = {}
#         rsp["code"] = 200
#         rsp["msg"] = msg
#         rsp["data"] = lst
#         rsp["total"] = total
#         return rsp
#
#     # 生成一个包含文本消息和数据的成功响应。
#     @staticmethod
#     def ok_resp_text(msg=None,data=None):
#         rsp = {}
#         rsp["code"] = 200
#         rsp["msg"] = msg
#         rsp["data"] = data
#         return rsp
#
#     # 新定义一个response模块，处理树形数据返回的。。。
#     # 生成用于返回树形数据的成功响应。
#     @staticmethod
#     def ok_resp_tree(treeData,msg):
#         rsp = {}
#         rsp["code"] = 200
#         rsp["msg"] = msg
#         rsp["data"] = treeData
#         return rsp
#
#     # 生成错误响应。
#     @staticmethod
#     def error_resp(msg):
#         rsp = {}
#         rsp["code"] = -1
#         rsp["msg"] = msg
#         return rsp
#
#     # 获取对象的自定义属性，过滤掉内置属性和方法。
#     def get_custom_attributes(self,obj):
#         custom_attributes = {}
#         # 获取对象的所有属性
#         attributes = vars(obj)
#         # 过滤掉内置属性和方法
#         for attribute, value in attributes.items():
#             if not attribute.startswith('__') and not callable(value) and not attribute.startswith('_'):
#                 custom_attributes[attribute] = value
#         return custom_attributes
#
#

# ============修改
import json
from flask import make_response
from datetime import datetime

# 自定义 JSON 编码器，处理 datetime 类型
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return super().default(obj)

class respModel:
    # 用于生成包含单个对象数据的成功响应。
    @staticmethod
    def ok_resp(obj=None, msg=None, dic_t=None):
        rsp = {}
        rsp["code"] = 200
        rsp["msg"] = msg
        data = {}
        if obj:
            data = respModel().get_custom_attributes(obj)
        if dic_t:
            data.update(dic_t)
        rsp["data"] = data
        return respModel._prepare_response(rsp)

    # 用于生成包含对象列表数据的成功响应，同时包含数据总数。
    @staticmethod
    def ok_resp_list(obj=None, msg=None, lst=None, total=0):
        rsp = {}
        rsp["code"] = 200
        rsp["msg"] = msg
        rsp["total"] = total
        lst1 = []
        if lst:
            for obj in lst:
                dic = respModel().get_custom_attributes(obj)
                lst1.append(dic)
        rsp["data"] = lst1
        return respModel._prepare_response(rsp)

    # 生成一个简单的成功响应，直接将传入的列表数据作为响应数据。
    @staticmethod
    def ok_resp_simple(lst=None, msg=None):
        rsp = {}
        rsp["code"] = 200
        rsp["msg"] = msg
        rsp["data"] = lst
        return respModel._prepare_response(rsp)

    # 生成一个简单的包含对象列表和总数的成功响应。
    @staticmethod
    def ok_resp_simple_list(lst=None, msg=None, total=0):
        rsp = {}
        rsp["code"] = 200
        rsp["msg"] = msg
        rsp["data"] = lst
        rsp["total"] = total
        return respModel._prepare_response(rsp)

    # 生成一个包含文本消息和数据的成功响应。
    @staticmethod
    def ok_resp_text(msg=None, data=None):
        rsp = {}
        rsp["code"] = 200
        rsp["msg"] = msg
        rsp["data"] = data
        return respModel._prepare_response(rsp)

    # 新定义一个response模块，处理树形数据返回的。。。
    # 生成用于返回树形数据的成功响应。
    @staticmethod
    def ok_resp_tree(treeData, msg):
        rsp = {}
        rsp["code"] = 200
        rsp["msg"] = msg
        rsp["data"] = treeData
        return respModel._prepare_response(rsp)

    # 生成错误响应。
    @staticmethod
    def error_resp(msg):
        rsp = {}
        rsp["code"] = -1
        rsp["msg"] = msg
        return respModel._prepare_response(rsp)

    # 获取对象的自定义属性，过滤掉内置属性和方法。
    def get_custom_attributes(self, obj):
        custom_attributes = {}
        # 获取对象的所有属性
        attributes = vars(obj)
        # 过滤掉内置属性和方法
        for attribute, value in attributes.items():
            if not attribute.startswith('__') and not callable(value) and not attribute.startswith('_'):
                custom_attributes[attribute] = value
        return custom_attributes

    # 准备响应，将数据转换为 JSON 字符串并设置响应头
    @staticmethod
    def _prepare_response(data):
        json_data = json.dumps(data, ensure_ascii=False, cls=CustomJSONEncoder).encode('utf-8')
        resp = make_response(json_data)
        resp.headers['Content-Type'] = 'application/json; charset=utf-8'
        return resp