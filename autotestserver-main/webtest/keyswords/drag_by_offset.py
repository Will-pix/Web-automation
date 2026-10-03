class drag_by_offset:
    """Drag element by pixel offset"""

    def __init__(self, driver):
        self.driver = driver

    def drag_by_offset(self, **kwargs):
        by_type = kwargs.get("by_type", "xpath")
        locator = kwargs.get("locator", "")
        x_offset = int(kwargs.get("x_offset", 0))
        y_offset = int(kwargs.get("y_offset", 0))
        if not locator:
            raise ValueError("Parameter 'locator' is required")
        by_map = {"xpath": By.XPATH, "id": By.ID, "name": By.NAME, "css selector": By.CSS_SELECTOR, "css": By.CSS_SELECTOR}
        by = by_map.get(by_type.lower(), By.XPATH)
        from selenium.webdriver.common.action_chains import ActionChains
        element = safe_find_visible_element(self.driver, by, locator)
        scroll_to_element(self.driver, element)
        ActionChains(self.driver).click_and_hold(element).move_by_offset(x_offset, y_offset).pause(0.3).release().perform()
        print(f"[Drag] Dragged by x:{x_offset} y:{y_offset}")
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException, ElementNotInteractableException
from web_base_utils import DEFAULT_TIMEOUT, MAX_RETRIES, RETRY_DELAY, scroll_to_element, safe_find_visible_element, safe_find_elements, safe_click, safe_input, wait_page_ready, dismiss_alerts_and_popups, try_find_with_fallbacks
