import os

from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait


class base_drag_and_drop:

    def __init__(self, driver):
        self.driver = driver

    def base_drag_and_drop(self, **kwargs):
        drag = kwargs["起始元素"]
        drop = kwargs["到达元素"]
        drag1 = self.find_element(drag)
        drop1 = self.find_element(drop)
        print("prag:", drag1)
        print("prop:", drop1)
        # ActionChains(self.driver).drag_and_drop(drag1, drop1).perform()
        # 获取元素坐标（本地与服务器对比）
        drag_rect = self.driver.execute_script("return arguments[0].getBoundingClientRect();", drag1)
        drop_rect = self.driver.execute_script("return arguments[0].getBoundingClientRect();", drop1)
        print(f"起始元素坐标（本地/服务器）: {drag_rect}")
        print(f"目标元素坐标（本地/服务器）: {drop_rect}")

        # 计算起始和目标元素的中心点
        start_x = drag_rect['left'] + drag_rect['width'] / 2
        start_y = drag_rect['top'] + drag_rect['height'] / 2
        target_x = drop_rect['left'] + drop_rect['width'] / 2
        target_y = drop_rect['top'] + drop_rect['height'] / 2
        print("起始x:",start_x)
        print("起始y:",start_y)
        print("终点x:",target_x)
        print("终点y:",target_y)


        actions = ActionChains(self.driver)

        # 1. 按住起始元素（不立即执行，加入队列）
        actions.click_and_hold(drag1)
        print("# 按住起始元素")
        actions.pause(3)

        # 2. 计算从起始点到目标点的绝对偏移量
        offset_x = target_x - start_x
        offset_y = target_y - start_y

        # 3. 应用Y轴修正（仅生产环境）
        flask_env = os.getenv('FLASK_ENV', 'development')
        if flask_env == 'production':
            offset_y += 110  # 修正Y轴偏移量
            print(f"应用Y轴修正: +110px，总偏移量: ({offset_x}, {offset_y})")
        else:
            print(f"本地环境，无Y轴修正，偏移量: ({offset_x}, {offset_y})")

        # 4. 移动到目标点（加入队列）
        actions.move_by_offset(offset_x, offset_y)
        actions.pause(3)
        print(f"移动到目标坐标: ({offset_x}, {offset_y})")

        # 5. 释放鼠标（加入队列）
        actions.release()
        print("# 释放鼠标")

        # 6. 一次性执行所有操作
        actions.perform()
        print("# 执行整个动作链")

        # 7. 执行js释放
        flask_env = os.getenv('FLASK_ENV', 'development')
        if flask_env == 'production':
            self._force_mouse_release()  # 强制释放
            print("生产环境，执行了释放")
        else:
            print("本地环境无需释放")

    def find_element(self, value):
        # 元素操作-输入内容
        by = 'xpath'
        value = value
        element = WebDriverWait(self.driver, timeout=30, poll_frequency=0.5, ignored_exceptions=None).until(
            lambda x: x.find_element(by=by, value=value))
        return element

    def _force_mouse_release(self):
        """通过JavaScript强制释放鼠标"""
        self.driver.execute_script("""
            if (document.documentElement.matches(':active')) {
                const event = new MouseEvent('mouseup', {
                    bubbles: true,
                    buttons: 0,
                    clientX: window.innerWidth / 2,
                    clientY: window.innerHeight / 2
                });
                document.dispatchEvent(event);
                window.requestAnimationFrame(() => {});
            }
        """)
        print("# 强制释放鼠标完成")