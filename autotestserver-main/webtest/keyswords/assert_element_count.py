class assert_element_count:
    """Assert the number of matched elements"""

    def __init__(self, driver):
        self.driver = driver

    def assert_element_count(self, **kwargs):
        by_type = kwargs.get("by_type", "xpath")
        locator = kwargs.get("locator", "")
        expected = int(kwargs.get("count", 1))
        op = kwargs.get("operator", "eq")
        if not locator:
            raise ValueError("Parameter 'locator' is required")
        by_map = {"xpath": By.XPATH, "css": By.CSS_SELECTOR, "class name": By.CLASS_NAME}
        by = by_map.get(by_type.lower(), By.XPATH)
        elements = safe_find_elements(self.driver, by, locator)
        actual = len(elements)
        op_map = {"eq": lambda a, e: a == e, "gt": lambda a, e: a > e, "lt": lambda a, e: a < e, "gte": lambda a, e: a >= e, "lte": lambda a, e: a <= e}
        if not op_map.get(op, op_map["eq"])(actual, expected):
            raise AssertionError(f"Element count mismatch: {actual} {op} {expected}")
        print(f"[Assert] Element count OK: {actual} {op} {expected}")
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException, ElementNotInteractableException
from web_base_utils import DEFAULT_TIMEOUT, MAX_RETRIES, RETRY_DELAY, scroll_to_element, safe_find_visible_element, safe_find_elements, safe_click, safe_input, wait_page_ready, dismiss_alerts_and_popups, try_find_with_fallbacks
