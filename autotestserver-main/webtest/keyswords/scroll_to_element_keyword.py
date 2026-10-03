class scroll_to_element_keyword:
    """Scroll element into view"""

    def __init__(self, driver):
        self.driver = driver

    def scroll_to_element_keyword(self, **kwargs):
        by_type = kwargs.get("by_type", "xpath")
        locator = kwargs.get("locator", "")
        block = kwargs.get("block", "center")
        if not locator:
            raise ValueError("Parameter 'locator' is required")
        by_map = {"xpath": By.XPATH, "id": By.ID, "css selector": By.CSS_SELECTOR, "css": By.CSS_SELECTOR, "class name": By.CLASS_NAME, "name": By.NAME}
        by = by_map.get(by_type.lower(), By.XPATH)
        element = safe_find_visible_element(self.driver, by, locator)
        scroll_to_element(self.driver, element, block=block)
        print(f"[Scroll] Scrolled to element: {by_type}={locator}")
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException, ElementNotInteractableException
from web_base_utils import DEFAULT_TIMEOUT, MAX_RETRIES, RETRY_DELAY, scroll_to_element, safe_find_visible_element, safe_find_elements, safe_click, safe_input, wait_page_ready, dismiss_alerts_and_popups, try_find_with_fallbacks
