class base_back_close_window:
    def __init__(self, driver):
        self.driver = driver

    def base_back_close_window(self,**kwargs):
        windows = self.driver.window_handles
        main = windows[0]
        for handle in windows:
            if handle != main:
                self.driver.switch_to.window(handle)
                self.driver.close()
        self.driver.switch_to.window(main)
