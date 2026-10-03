import os
import requests
import json
from selenium.webdriver import ActionChains
import base64
from selenium.webdriver.common.by import By
from webtest.keyswords.ai_runtime import apply_runtime_api_key, build_headers


class ai_drag_drop:
    def __init__(self, driver):
        self.driver = driver

    def ai_drag_drop(self,  **kwargs):
        ai_step = kwargs["ai_step"]

        # 截图并转为Base64
        screenshot = self.driver.get_screenshot_as_png()
        screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')

        # 调用模型获取坐标
        ai_config = apply_runtime_api_key()
        coords_str = self._get_drag_coordinates(ai_step, screenshot_b64, ai_config)
        coords_dict = json.loads(coords_str)

        # 获取浏览器窗口高度信息
        window_height = self.driver.get_window_size()["height"]
        content_height = self.driver.execute_script("return window.innerHeight")
        nav_height = window_height - content_height

        # 解析坐标
        start_x1 = coords_dict["start_x1"]
        start_x2 = coords_dict["start_x2"]
        start_y1 = coords_dict["start_y1"]
        start_y2 = coords_dict["start_y2"]

        end_x1 = coords_dict["end_x1"]
        end_x2 = coords_dict["end_x2"]
        end_y1 = coords_dict["end_y1"]
        end_y2 = coords_dict["end_y2"]

        # 计算中心点
        start_x_center = (start_x1 + start_x2) / 2
        start_y_center = (start_y1 + start_y2) / 2

        end_x_center = (end_x1 + end_x2) / 2
        end_y_center = (end_y1 + end_y2) / 2

        # 屏幕分辨率
        screen_width = 1920
        screen_height = int(content_height)

        # 计算实际屏幕坐标
        start_abs_x = (start_x_center / 1000) * screen_width
        start_abs_y = (start_y_center / 1000) * screen_height

        end_abs_x = (end_x_center / 1000) * screen_width
        end_abs_y = (end_y_center / 1000) * screen_height

        print("起始坐标:", start_abs_x, start_abs_y)
        print("终点坐标:", end_abs_x, end_abs_y)

        # 创建临时元素作为拖拽参考点
        self.driver.execute_script("""
            const origin = document.createElement('div');
            origin.id = 'viewport-origin';
            origin.style = 'position:fixed;left:0;top:0;width:1px;height:1px;z-index:9999';
            document.body.appendChild(origin);
        """)

        origin = self.driver.find_element(By.ID, 'viewport-origin')

        # 执行拖拽操作
        actions = ActionChains(self.driver)
        actions.move_to_element_with_offset(origin, start_abs_x, start_abs_y)
        actions.click_and_hold()
        actions.move_to_element_with_offset(origin, end_abs_x, end_abs_y)
        actions.release()
        actions.perform()

        # 移除临时元素
        self.driver.execute_script("document.getElementById('viewport-origin').remove();")

    def _get_drag_coordinates(self, ai_step, screenshot_b64, ai_config):
        prompt = f"""
        需求：按照指令描述查找起始元素和目标位置的坐标，用于拖拽操作
        指令：{ai_step}
        返回格式为包含起始和终点坐标的字典：
        {{"start_x1": 数字, "start_y1": 数字, "start_x2": 数字, "start_y2": 数字, 
        "end_x1": 数字, "end_y1": 数字, "end_x2": 数字, "end_y2": 数字}}
        """

        response = requests.post(
            f"{ai_config['api_base']}{ai_config['request_path']}",
            headers=build_headers(ai_config),
            json={
                "model": ai_config["model_name"],
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{screenshot_b64}"
                                },
                                "detail": "high"
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ],
                "thinking": {
                    "type": "disabled"
                },
                "image_pixel_limit": {
                    "max_pixels": 4014080,
                    "min_pixels": 3136
                }
            }
        )

        # 模型调用失败直接抛异常
        if response.status_code != 200:
            print("模型调用失败")
            assert 1 == 2

        content = response.json()["choices"][0]["message"]["content"].strip()
        if not (content.startswith('{') and content.endswith('}')):
            print("模型返回非JSON格式")
            assert 1 == 2

        print("拖拽坐标返回值:", content)
        return content
