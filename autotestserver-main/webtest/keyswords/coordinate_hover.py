import time

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By


class coordinate_hover:
    def __init__(self, driver):
        self.driver = driver

    # 方法入口
    def coordinate_hover(self, **kwargs):
        x = int(kwargs["x"])
        # y = int(kwargs["y"]) -112
        y = int(kwargs["y"])

        # 创建一个固定在视口左上角的临时元素
        self.driver.execute_script("""
            const origin = document.createElement('div');
            origin.id = 'viewport-origin';
            origin.style = 'position:fixed;left:0;top:0;width:1px;height:1px;z-index:9999';
            document.body.appendChild(origin);
        """)
        # 定位这个元素并基于它点击
        origin = self.driver.find_element(By.ID, 'viewport-origin')
        ActionChains(self.driver).move_to_element_with_offset(origin, x, y).perform()
        time.sleep(0.5)  # 悬停等待（如需触发下拉菜单等效果）

        # 删除临时元素1813  147
        self.driver.execute_script("document.getElementById('viewport-origin').remove();")
