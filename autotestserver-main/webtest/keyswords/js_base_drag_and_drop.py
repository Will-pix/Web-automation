import os
import time

from selenium.webdriver.support.wait import WebDriverWait


class js_base_drag_and_drop:
    def __init__(self, driver):
        self.driver = driver

    def js_base_drag_and_drop(self, **kwargs):
        drag = kwargs["起始元素"]
        drop = kwargs["到达元素"]
        drag1 = self.find_element(drag)
        drop1 = self.find_element(drop)

        # 获取元素坐标
        drag_rect = self.driver.execute_script("return arguments[0].getBoundingClientRect();", drag1)
        drop_rect = self.driver.execute_script("return arguments[0].getBoundingClientRect();", drop1)

        # 计算拖拽坐标
        start_x = drag_rect['left'] + drag_rect['width'] / 2
        start_y = drag_rect['top'] + drag_rect['height'] / 2
        target_x = drop_rect['left'] + drop_rect['width'] / 2
        target_y = drop_rect['top'] + drop_rect['height'] / 2

        # 打印坐标信息（Python日志）
        print(f"拖拽坐标计算: 起始({start_x:.1f}, {start_y:.1f}) → 目标({target_x:.1f}, {target_y:.1f})")

        # 应用 Y 轴修正（仅生产环境）
        if os.getenv('FLASK_ENV') == 'production':
            target_y += 110
            print(f"生产环境: 目标Y坐标修正为 {target_y:.1f}")

        # 执行拖拽步骤（添加延迟便于观察）
        print("开始执行拖拽...")
        self.js_mouse_down(start_x, start_y)  # 步骤1：按住
        time.sleep(1)

        self.js_mouse_move(target_x, target_y)  # 步骤2：移动
        time.sleep(1)

        self.js_mouse_up(target_x, target_y)  # 步骤3：释放
        print("✅ 拖拽操作已完成")

    def js_mouse_down(self, x, y):
        """触发mousedown事件并添加日志"""
        self.driver.execute_script("""
            console.log('[JS] 准备触发mousedown事件 at', arguments[0], arguments[1]);
            const e = new MouseEvent('mousedown', {
                bubbles: true,
                clientX: arguments[0],
                clientY: arguments[1],
                buttons: 1
            });
            document.elementFromPoint(arguments[0], arguments[1]).dispatchEvent(e);
            console.log('[JS] mousedown事件已触发 ✅');
        """, x, y)

    def js_mouse_move(self, x, y):
        """触发mousemove事件并添加日志"""
        self.driver.execute_script("""
            console.log('[JS] 准备触发mousemove事件 to', arguments[0], arguments[1]);
            const e = new MouseEvent('mousemove', {
                bubbles: true,
                clientX: arguments[0],
                clientY: arguments[1],
                buttons: 1
            });
            document.elementFromPoint(arguments[0], arguments[1]).dispatchEvent(e);
            console.log('[JS] mousemove事件已触发 ✅');
        """, x, y)

    def js_mouse_up(self, x, y):
        """触发mouseup事件并添加日志"""
        self.driver.execute_script("""
            console.log('[JS] 准备触发mouseup事件 at', arguments[0], arguments[1]);
            const e = new MouseEvent('mouseup', {
                bubbles: true,
                clientX: arguments[0],
                clientY: arguments[1],
                buttons: 0
            });
            document.elementFromPoint(arguments[0], arguments[1]).dispatchEvent(e);
            console.log('[JS] mouseup事件已触发 ✅');
        """, x, y)

    def find_element(self, value):
        by = 'xpath'
        print(f"查找元素: {value} (By: {by})")
        element = WebDriverWait(self.driver, timeout=30, poll_frequency=0.5, ignored_exceptions=None).until(
            lambda x: x.find_element(by=by, value=value)
        )
        print(f"✅ 元素已找到: {value}")
        return element