class coordinate_smart_click:
    """Click at viewport coordinates using anchor element"""

    def __init__(self, driver):
        self.driver = driver

    def coordinate_smart_click(self, **kwargs):
        x = int(kwargs.get("x", 0))
        y = int(kwargs.get("y", 0))
        click_count = int(kwargs.get("click_count", 1))
        interval = float(kwargs.get("interval", 0.2))
        if x <= 0 or y <= 0:
            raise ValueError("Parameters 'x' and 'y' must be positive")
        self.driver.execute_script('var a=document.createElement("div");a.id="__ca__";a.style="position:fixed;left:0;top:0;width:1px;height:1px;z-index:99999;pointer-events:none";document.body.appendChild(a);')
        anchor = self.driver.find_element(By.ID, '__ca__')
        try:
            from selenium.webdriver.common.action_chains import ActionChains
            for i in range(click_count):
                ActionChains(self.driver).move_to_element_with_offset(anchor, x, y).click().perform()
                if click_count > 1 and i < click_count - 1:
                    time.sleep(interval)
            print(f"[CoordClick] ({x}, {y}) clicked {click_count} time(s)")
        finally:
            self.driver.execute_script('var a=document.getElementById("__ca__");if(a)a.remove();')

import time
from selenium.webdriver.common.by import By
