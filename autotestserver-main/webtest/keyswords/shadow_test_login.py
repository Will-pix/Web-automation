import json
import requests
import warnings


class shadow_test_login:

    def __init__(self, driver):
        self.driver = driver
        # 忽略SSL警告
        warnings.filterwarnings("ignore", category=UserWarning)

    def shadow_test_login(self, **kwargs):
        dev = kwargs["dev"]
        target_url = kwargs["目标对象"]
        login_data = json.loads(kwargs["数据内容"])

        if dev == 'test':
        # 测试环境
            target_url1 = "https://shadow-test.yangcong345.com/api/auth/me"
            login_url = "https://shadow-test.yangcong345.com/api/auth/inner/test/login"

        elif dev == 'stage':
        # 预发布环境
            target_url1 = "https://shadow-stage.yangcong345.com/api/auth/me"
            login_url = "https://shadow-stage.yangcong345.com/api/auth/inner/test/login"

        elif dev == 'online':
        # 生产环境
            target_url1 = "https://shadow.yangcong345.com/api/auth/me"
            login_url = "https://shadow.yangcong345.com/api/auth/inner/test/login"

        # 默认test
        else:
            target_url1 = "https://shadow-test.yangcong345.com/api/auth/me"
            login_url = "https://shadow-test.yangcong345.com/api/auth/inner/test/login"


        self.driver.get(target_url1)

        # 获取传入的登录数据和URL
        # 发送登录请求获取token
        response = requests.post(login_url, json=login_data)
        response_data = response.json()
        msg = response_data["shadowToken"]
        token = "Bearer " + msg
        # 获取metoken
        header = {"ShadowAuthorization": token, "Authorization": token}
        metoken = requests.get(url=target_url1,
            headers=header,
            verify=False
        )
        value = metoken.headers["ShadowAuthorization"]
        print("value的值为：", value)
        # 写入localStorage（此时已阻止跳转，域名保持在目标源）
        self.driver.execute_script("""
	        window.localStorage.setItem('ShadowAuthorization', arguments[0]);
	    """, value)

        # 访问目标页面
        self.driver.get(target_url)
        # 验证localStorage是否写入成功
