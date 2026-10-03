class swipe_screen:
    """Simulate finger swipe on screen (works on PC too)"""

    def __init__(self, driver):
        self.driver = driver

    def swipe_screen(self, **kwargs):
        from selenium.webdriver.common.action_chains import ActionChains
        start_x = int(kwargs.get("start_x", 500))
        start_y = int(kwargs.get("start_y", 500))
        end_x = int(kwargs.get("end_x", 500))
        end_y = int(kwargs.get("end_y", 100))
        duration_ms = int(kwargs.get("duration_ms", 500))
        ActionChains(self.driver).move_by_offset(start_x, start_y).click_and_hold().move_by_offset(end_x - start_x, end_y - start_y).pause(duration_ms / 1000.0).release().perform()
        ActionChains(self.driver).move_by_offset(-end_x, -end_y).perform()
        print(f"[Swipe] From ({start_x},{start_y}) to ({end_x},{end_y})")