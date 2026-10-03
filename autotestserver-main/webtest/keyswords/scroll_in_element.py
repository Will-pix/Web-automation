class scroll_in_element:
    """Scroll inside a specific element"""

    def __init__(self, driver):
        self.driver = driver

    def scroll_in_element(self, **kwargs):
        by_type = kwargs.get("by_type", "xpath")
        locator = kwargs.get("locator", "")
        x_dist = int(kwargs.get("x_distance", 0))
        y_dist = int(kwargs.get("y_distance", 100))
        if not locator:
            raise ValueError("Parameter 'locator' is required")
        by_map = {"xpath": By.XPATH, "css": By.CSS_SELECTOR, "id": By.ID}
        by = by_map.get(by_type.lower(), By.XPATH)
        element = safe_find_visible_element(self.driver, by, locator)
        self.driver.execute_script(f"arguments[0].scrollBy({{left: {x_dist}, top: {y_dist}, behavior: 'smooth'}});", element)
        print(f"[Scroll] Inside element scrolled x:{x_dist} y:{y_dist}")
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException, ElementNotInteractableException
from web_base_utils import DEFAULT_TIMEOUT, MAX_RETRIES, RETRY_DELAY, scroll_to_element, safe_find_visible_element, safe_find_elements, safe_click, safe_input, wait_page_ready, dismiss_alerts_and_popups, try_find_with_fallbacks
