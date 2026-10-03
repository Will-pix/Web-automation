# import jwt
# import app
# import datetime
#
# class JwtUtils(object):
#
#     @staticmethod
#     def create_token(username,password):
#         key = app.application.config["SECRET_KEY"]
#         # 要吧什么东西转换成token
#         payload ={
#             "username":username,
#             "password":password,
#             "exp":datetime.datetime.utcnow()+datetime.timedelta(minutes=5) #设置过期时间为五分钟
#         }
#         token = jwt.encode(payload,key,algorithm="HS256")
#         return token
#
#     @staticmethod
#     def verify_token(token):
#         key = app.app.config["SECRET_KEY"]
#         try:
#             payload = jwt.decode(token,key,algorithms=['HS256'])
#             print(payload)
#         except jwt.InvalidTokenError:
#             print("无法校验的token")

import jwt
# import app
import datetime
from flask import g, current_app

class JwtUtils(object):

    @staticmethod
    def create_token(access_user_id,access_name,access_email):
        key = current_app.config["SECRET_KEY"]
        # 要吧什么东西转换成token
        payload ={
            "access_user_id":access_user_id,
            "access_name":access_name,
            "access_email":access_email,
            "exp":datetime.datetime.utcnow()+datetime.timedelta(minutes=10080) #设置过期时间为五分钟
        }
        token = jwt.encode(payload,key,algorithm="HS256")

        return token

    @staticmethod
    def verify_token(token):
        # print("执行了token验证")
        key = current_app.config["SECRET_KEY"]
        try:
            payload = jwt.decode(token,key,algorithms=['HS256'])
            # print("解密token:",payload)
            return(payload)
        except jwt.InvalidTokenError:
            print("无法校验的token")
            return None
