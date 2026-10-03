class coordinate_smart_input:
    """Click at coordinates then input text into focused element"""

    def __init__(self, driver):
        self.driver = driver

    def coordinate_smart_input(self, **kwargs):
        x = int(kwargs.get("x", 0))
        y = int(kwargs.get("y", 0))
        text = kwargs.get("text", "")
        self.driver.execute_script('var a=document.createElement("div");a.id="__ca__";a.style="position:fixed;left:0;top:0;width:1px;height:1px;z-index:99999;pointer-events:none";document.body.appendChild(a);')
        anchor = self.driver.find_element(By.ID, '__ca__')
        try:
            from selenium.webdriver.common.action_chains import ActionChains
            from selenium.webdriver.common.keys import Keys
            ActionChains(self.driver).move_to_element_with_offset(anchor, x, y).click().perform()
            time.sleep(0.3)
            active = self.driver.switch_to.active_element
            if active and active != self.driver.find_element(By.TAG_NAME, "body"):
                active.send_keys(Keys.CONTROL, "a")
                active.send_keys(Keys.BACKSPACE)
                active.send_keys(text)
                print(f"[CoordInput] Typed: '{text}'")
            else:
                print("[CoordInput] Warning: no active input element at coordinates")
        finally:
            self.driver.execute_script('var a=document.getElementById("__ca__");if(a)a.remove();')

import time
from selenium.webdriver.common.by import By
