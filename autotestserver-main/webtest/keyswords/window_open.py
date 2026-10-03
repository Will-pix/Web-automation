class window_open:

    def __init__(self, driver):
        self.driver = driver
    # 打开新窗口
    def window_open(self, **kwargs):
        url = kwargs["url"]
        self.driver.execute_script(f"window.open('{url}');")