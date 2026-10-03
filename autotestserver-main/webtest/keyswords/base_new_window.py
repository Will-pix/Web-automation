from time import sleep
class base_new_window:
    def __init__(self, driver):
        self.driver = driver
    # 查找元素方法封装
    def base_new_window(self,**kwargs):
        window = self.driver.window_handles[-1]
        self.driver.switch_to.window(window)
        sleep(1)

