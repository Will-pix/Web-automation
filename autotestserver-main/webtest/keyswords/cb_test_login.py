import json
import requests

class cb_test_login:

    def __init__(self, driver):
        self.driver = driver

    def cb_test_login(self, **kwargs):

        # 传入的值
        data = json.loads(kwargs["数据内容"])
        tokenurln = kwargs["目标对象"]

        response = requests.post(url=tokenurln, json=data,verify=False)
        responsee = response.json()
        msg = responsee["shadowToken"]
        print("获取shadowtoken并构造cookie的msg为:", msg)
        header = {"ShadowAuthorization": msg, "Authorization": msg}
        metoken = requests.get("https://shadow-test.yangcong345.com/api/auth/me", headers=header, verify=False)

        print(metoken.headers)
        value = metoken.headers["ShadowAuthorization"]
        print("value的值为：", value)
        msg = responsee["shadowToken"]
        msg3 = {"name": "onionsToken", "value": "{}".format(value)}
        msg4 = {"name": "shadowToken", "value": "{}".format(value)}
        print("携带shadowtiken请求me接口，并获取构造token的mg3为：", msg3)
        print("携带shadowtiken请求me接口，并获取构造token的mg4为：", msg4)
        self.driver.add_cookie(msg3)
        self.driver.add_cookie(msg4)

        # # 预期值
        # target = kwargs["数据内容"]
        # # 当前值
        # current = self.driver.find_element(kwargs["定位方式"], kwargs["目标对象"]).text
        # print(f"判断是否相等,{target} - {current}")
        # assert current == target