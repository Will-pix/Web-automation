class assert_element_visible:
    """Assert that an element is visible on the page"""

    def __init__(self, driver):
        self.driver = driver

    def assert_element_visible(self, **kwargs):
        by_type = kwargs.get("by_type", "xpath")
        locator = kwargs.get("locator", "")
        timeout = int(kwargs.get("timeout", DEFAULT_TIMEOUT))
        if not locator:
            raise ValueError("Parameter 'locator' is required")
        by_map = {"xpath": By.XPATH, "id": By.ID, "name": By.NAME, "css selector": By.CSS_SELECTOR, "css": By.CSS_SELECTOR, "class name": By.CLASS_NAME, "tag name": By.TAG_NAME}
        by = by_map.get(by_type.lower(), By.XPATH)
        try:
            WebDriverWait(self.driver, timeout, 0.5).until(EC.visibility_of_element_located((by, locator)))
            print(f"[Assert] Element visible: {by_type}={locator}")
        except TimeoutException:
            raise AssertionError(f"Element not visible: {by_type}={locator} (timeout {timeout}s)")
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException, ElementNotInteractableException
from web_base_utils import DEFAULT_TIMEOUT, MAX_RETRIES, RETRY_DELAY, scroll_to_element, safe_find_visible_element, safe_find_elements, safe_click, safe_input, wait_page_ready, dismiss_alerts_and_popups, try_find_with_fallbacks
