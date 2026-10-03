import os
import requests
import json
from flask import current_app
from selenium.webdriver import ActionChains, Keys
import time
import base64

from selenium.webdriver.common.by import By
from webtest.keyswords.ai_runtime import get_runtime_ai_settings

class ai_input_image_no:
    def __init__(self, driver):
        self.driver = driver

    # 方法入口
    def ai_input_image_no(self, **kwargs):
        # API Key is now managed via config

        ai_step = kwargs["ai_step"]
        # 先处理语义化理解
        input_value = self.input_Analysis(ai_step)

        # 截图并转为Base64
        screenshot = self.driver.get_screenshot_as_png()
        screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')

        # 调用模型获取坐标
        coords_str = self.get_coordinates(ai_step, screenshot_b64)
        coords_dict = json.loads(coords_str)

        # 获取浏览器窗口总高度（含导航栏）
        window_height = self.driver.get_window_size()["height"]  # 比如 1080px
        print("浏览器窗口总高度",window_height)
        #
        # 获取网页内容区域高度（不含导航栏）
        content_height = self.driver.execute_script("return window.innerHeight")
        print("网页内容区域高度",content_height)

        # 计算导航栏高度
        nav_height = window_height - content_height  # 通常在 60-100px 左右（因浏览器版本/系统而异）
        print("导航栏高度",nav_height)


        # # 解析坐标（进行固定分辨率转换）
        print("返回坐标",coords_dict)
        x1 = coords_dict["x1"]
        x2 = coords_dict["x2"]
        y1 = coords_dict["y1"]
        y2 = coords_dict["y2"]

        # 假设模型返回的坐标是 (x1, y1, x2, y2)
        x_center = (x1 + x2) / 2  # 计算中心点 x 坐标
        y_center = (y1 + y2) / 2  # 计算中心点 y 坐标

        # 屏幕分辨率
        screen_width = 1920
        screen_height = int(content_height)

        # 计算实际屏幕坐标
        abs_x = (x_center / 1000) * screen_width
        abs_y = (y_center / 1000) * screen_height

        print("abs_x", abs_x)
        print("abs_y", abs_y)

        # 按截图工具对比Y需要减去112

        """这是相对与一个元素的坐标点击"""
        # 创建一个固定在视口左上角的临时元素
        self.driver.execute_script("""
            const origin = document.createElement('div');
            origin.id = 'viewport-origin';
            origin.style = 'position:fixed;left:0;top:0;width:1px;height:1px;z-index:9999';
            document.body.appendChild(origin);
        """)
        # 定位这个元素并基于它点击
        origin = self.driver.find_element(By.ID, 'viewport-origin')
        ActionChains(self.driver).move_to_element_with_offset(origin, abs_x, abs_y).click().perform()
        time.sleep(0.5)  # 等待输入框激活
        # flask_env = os.getenv('FLASK_ENV', 'development')
        # if flask_env == 'production':
        #     ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
        # else:
        #     ActionChains(self.driver).key_down(Keys.COMMAND).send_keys('a').key_up(Keys.COMMAND).perform()
        # ActionChains(self.driver).send_keys(Keys.DELETE).perform()
        # # 输入新内容
        # 调用模型拆解内容
        ActionChains(self.driver).send_keys(input_value).perform()

        # 移除临时元素
        self.driver.execute_script("document.getElementById('viewport-origin').remove();")


    # 调用模型获取坐标
    def get_coordinates(self, ai_step, screenshot_b64):
        prompt = f"""
        需求：按照指令描述查找交互元素的坐标位置方便后续操作，
        指令：{ai_step}
        返回bbox格式为字典：{{"x1": 数字, "y1": 数字，"x2": 数字, "y2": 数字}}
        """
        # thinking disabled
        response = requests.post(
            f"{get_runtime_ai_settings()['api_base']}/chat/completions",
            headers={
                "Authorization": f"Bearer {current_app.config.get('OPENAI_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "model": get_runtime_ai_settings()["vision_model"],
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {

                                    "url":  f"data:image/png;base64,{screenshot_b64}"},
                                    "detail":"high"
                            },{
                                "type": "text",
                                "text": prompt,
                            }
                        ]
                    }
                ]
                ,
                "thinking":{
                    "type":"disabled"
                    }
                ,
                "image_pixel_limit": {
        "max_pixels": 4014080,
        "min_pixels": 3136
        }
            }
        )
        # print(response.request.body)
        xpath = response.json()
        xpath_value = response.json()["choices"][0]["message"]["content"]
        print("豆包返回值:", xpath)
        print("豆包精准值:", xpath_value)

        # 模型调用失败直接抛异常
        if response.status_code != 200:
            print("模型调用失败")
            assert 1 == 2

        content = response.json()["choices"][0]["message"]["content"].strip()
        if not (content.startswith('{') and content.endswith('}')):
            print("模型返回非JSON格式")
            assert 1 == 2

        return content


  # 实际值提取
    def input_Analysis(self,ai_step):
        prompt = f"""
        任务：从用户指令中提取需要输入的具体内容

        用户指令：
        {ai_step}

        提取要求：
        1. 忽略操作词（如"输入"、"搜索"、"查询"等）
        2. 提取核心输入内容（如ID、关键词、文本等）
        3. 保留完整语义（如"今天天气"而非"今天"）
        4. 若指令中无明确输入内容，返回空字符串

        输出要求：纯文本，无需解释
        """
        # 调用大模型API-个人
        # response = requests.post(
        #     "https://api.deepseek.com/v1/chat/completions",
        #     headers={
        #         "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
        #         "Content-Type": "application/json"
        #     },
        #     json={
        #         "model": "deepseek-chat",
        #         "messages": [{"role": "user", "content": prompt}],
        #         "temperature": 0.1,
        #         "max_tokens": 100
        #     }
        # )
        # 调用大模型API-公司豆包1.6
        response = requests.post(
            f"{get_runtime_ai_settings()['api_base']}/chat/completions",
            headers={
                "Authorization": f"Bearer {current_app.config.get('OPENAI_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "model": get_runtime_ai_settings()["text_model"],
                "messages": [
                    {
                        "role": "user",
                        "content":[
                            {
                                "text": prompt,
                                "type": "text"
                            }
                        ]
                    }
                ],
                "thinking":{
                "type":"disabled"
                }
            }
        )
        try:
            print("用户指令中提取需要输入的具体内容为:",response.json())
            return response.json()["choices"][0]["message"]["content"].strip()
        except:
            # 失败时使用启发式提取
            print("模型未能获取成功")
            return "模型未能获取成功"

