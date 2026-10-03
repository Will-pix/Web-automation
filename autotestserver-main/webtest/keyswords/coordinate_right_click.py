class coordinate_right_click:
    """Right click at viewport coordinates"""

    def __init__(self, driver):
        self.driver = driver

    def coordinate_right_click(self, **kwargs):
        x = int(kwargs.get("x", 0))
        y = int(kwargs.get("y", 0))
        self.driver.execute_script('var a=document.createElement("div");a.id="__ca__";a.style="position:fixed;left:0;top:0;width:1px;height:1px;z-index:99999;pointer-events:none";document.body.appendChild(a);')
        anchor = self.driver.find_element(By.ID, '__ca__')
        try:
            from selenium.webdriver.common.action_chains import ActionChains
            ActionChains(self.driver).move_to_element_with_offset(anchor, x, y).context_click().perform()
            print(f"[CoordRightClick] ({x}, {y})")
        finally:
            self.driver.execute_script('var a=document.getElementById("__ca__");if(a)a.remove();')

from selenium.webdriver.common.by import By
