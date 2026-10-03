
class refresh:

    def __init__(self, driver):
        self.driver = driver
    # 刷新
    def refresh(self, **kwargs):
        # 使用 value 属性获取按钮文本
        self.driver.refresh()
