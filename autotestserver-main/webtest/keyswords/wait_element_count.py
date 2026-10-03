class wait_element_count:
    """Wait until a specified number of elements appear"""

    def __init__(self, driver):
        self.driver = driver

    def wait_element_count(self, **kwargs):
        by_type = kwargs.get("by_type", "xpath")
        locator = kwargs.get("locator", "")
        count = int(kwargs.get("count", 1))
        timeout = int(kwargs.get("timeout", DEFAULT_TIMEOUT))
        if not locator:
            raise ValueError("Parameter 'locator' is required")
        by_map = {"xpath": By.XPATH, "css": By.CSS_SELECTOR, "class name": By.CLASS_NAME}
        by = by_map.get(by_type.lower(), By.XPATH)
        try:
            WebDriverWait(self.driver, timeout, 0.5).until(lambda d: len(d.find_elements(by, locator)) >= count)
            actual = len(self.driver.find_elements(by, locator))
            print(f"[Wait] Found {actual} elements (expected >= {count})")
        except TimeoutException:
            actual = len(self.driver.find_elements(by, locator))
            raise TimeoutException(f"Only {actual} elements found after {timeout}s (expected >= {count})")
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException, ElementNotInteractableException
from web_base_utils import DEFAULT_TIMEOUT, MAX_RETRIES, RETRY_DELAY, scroll_to_element, safe_find_visible_element, safe_find_elements, safe_click, safe_input, wait_page_ready, dismiss_alerts_and_popups, try_find_with_fallbacks
