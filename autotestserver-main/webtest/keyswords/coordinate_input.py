import os
import platform

from selenium.webdriver import ActionChains, Keys
import time

from selenium.webdriver.common.by import By



class coordinate_input:
    def __init__(self, driver):
        self.driver = driver

    # 方法入口
    def coordinate_input(self, **kwargs):
        x = int(kwargs["x"])
        y = int(kwargs["y"])
        # y = int(kwargs["y"]) - 112

        input_value = kwargs["数据内容"]

        # self._reset_mouse_to_origin()
        # 创建一个固定在视口左上角的临时元素
        self.driver.execute_script("""
            const origin = document.createElement('div');
            origin.id = 'viewport-origin';
            origin.style = 'position:fixed;left:0;top:0;width:1px;height:1px;z-index:9999';
            document.body.appendChild(origin);
        """)
        # 定位这个元素并基于它点击
        origin = self.driver.find_element(By.ID, 'viewport-origin')
        actions = ActionChains(self.driver)

        # 点击目标位置
        time.sleep(1)
        ActionChains(self.driver).move_to_element_with_offset(origin, x, y).click().perform()
        time.sleep(0.5)  # 等待输入框激活
        flask_env = os.getenv('FLASK_ENV', 'development')
        if flask_env == 'production':
            actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
        else:
            actions.key_down(Keys.COMMAND).send_keys('a').key_up(Keys.COMMAND).perform()
        actions.send_keys(Keys.DELETE).perform()
        # 输入新内容
        actions.send_keys(input_value).perform()

        # 删除临时元素
        self.driver.execute_script("document.getElementById('viewport-origin').remove();")