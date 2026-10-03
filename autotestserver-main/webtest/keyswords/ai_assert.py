import base64
import json
import os
import requests
from bs4 import BeautifulSoup, NavigableString
from selenium.webdriver.support.wait import WebDriverWait
import time
from webtest.keyswords.ai_runtime import get_runtime_ai_settings


class ai_assert:

    def __init__(self, driver):
        self.driver = driver

    # 方法入口
    def ai_assert(self, **kwargs):
        ai_step = kwargs["ai_step"]
        print("接收到的断言值",ai_step)
        pass
        # 调用解析语义
        action_step = self.ai_assert_Analysis_aciton(ai_step)
        # 调用上传模型判断
        verify_value = self.ai_assert_scrrenshot(action_step)
        # 判断
        self.ai_assert_verify(verify_value)

    # 使用模型语义分析判断
    def ai_assert_Analysis_aciton(self, ai_step):
        os.environ["OPENAI_API_KEY"] = get_runtime_ai_settings()["api_key"]
        prompt = f"""
        任务：从用户指令中分析用户想要执行的步骤数量及每个步骤要执行的类型

        用户指令：
        {ai_step}

        分析要求：
        1. 分析用户总要执行的步骤，进行文本切割
        2. 根据步骤分析用户要操作的类型，并归类，类型仅有七个，点击，输入，悬停，拖拽，滑动，等待，断言，如果无法分类都归为点击
        3. 保留完整语义（如"今天天气"而非"今天"）,只进行拆分步骤和补充类型
        输出要求-列表套字典：[{{"order":顺序,"type":"类型","step":"切割的步骤信息"}}]
        """
        # 调用大模型API-豆包1.6
        response = requests.post(
            f"{get_runtime_ai_settings()['api_base']}/chat/completions",
            headers={
                "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
                "Content-Type": "application/json"
            },
            json={
                "model": get_runtime_ai_settings()["text_model"],
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
            }
        )
        try:
            print("用户指令中提取需要输入的具体内容为:", response.json())
            return response.json()["choices"][0]["message"]["content"].strip()
        except:
            # 失败时使用启发式提取
            print("模型未能获取成功")
            return "模型未能获取成功"

    # 携带图片与断言预期值请求模型查看是否合规，模型返回规则成立于不成立的论证
    def ai_assert_scrrenshot(self, step):
        screenshot = self.driver.get_screenshot_as_png()
        screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')
        os.environ["OPENAI_API_KEY"] = get_runtime_ai_settings()["api_key"]
        prompt = f"""
        需求：判断用户断言是否正确并确定类型，需：1. 精准提取核心语义与关键对象；2. 按统一规则对比；3. 输出简洁无冗余。
        步骤1：提取【核心语义】+【关键对象】：
          - 核心语义：用户主张的页面状态；
          - 关键对象：核心语义中“被判断的核心元素”（即判断的聚焦点）；
          （统一规则：若核心语义提及“结果/数值/答案”，关键对象默认是“最终结果/数值”；若提及“显示内容/文本”，关键对象默认是“完整显示文本”）。
        步骤2：明确【实际结果】+【关键对象对应值】：
          - 实际结果：页面真实状态；
          - 关键对象对应值：实际结果中，与“核心语义关键对象”属性匹配的元素（即实际状态中对应关键对象的具体内容）。
        步骤3：判断（基于统一规则）：
          （1）断言类型：
              - 核心语义主张“实际结果的关键对象对应值 = 某目标”→“相等”；
              - 核心语义主张“实际结果的关键对象对应值 ≠ 某目标”→“不相等”；
              - 核心语义涉及“某内容是否存在于页面”→“包含/不包含”。
          （2）结果（仅基于关键对象对应值与目标的对比）：
              - “相等”类型：关键对象对应值与目标一致→正确；否则→错误；
              - “不相等”类型：关键对象对应值与目标不一致→正确；否则→错误。

        用户指令：{step}
        返回格式（严格字典，原因分点简洁）：
        {{"结果":"正确/错误","断言类型":"相等/不相等/包含/不包含","原因":"1.核心语义（关键对象：xxx）：xxx；2.实际结果（关键对象对应值：xxx）：xxx；3.类型依据：xxx；4.结果依据：关键对象对应值与目标一致/不一致"}}
        """
        response = requests.post(
            f"{get_runtime_ai_settings()['api_base']}/chat/completions",
            headers={
                "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
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

                                    "url": f"data:image/png;base64,{screenshot_b64}"},
                                "detail": "high"
                            }, {
                                "type": "text",
                                "text": prompt,
                            }
                        ]
                    }
                ]
                ,
                "thinking": {
                    "type": "disabled"
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
        return xpath_value

    # 判断模型是否成立，成立通过，不成立失败
    def ai_assert_verify(self,verify_value):
        verify_dict = json.loads(verify_value)
        result = verify_dict["结果"]
        if result == "正确":
            pass
        else:
            assert 1 == 2
