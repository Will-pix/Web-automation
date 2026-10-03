class wait_url_contains:
    """Wait until the URL contains a specific string (page navigation complete)"""

    def __init__(self, driver):
        self.driver = driver

    def wait_url_contains(self, **kwargs):
        url_part = kwargs.get("url_part", "")
        timeout = int(kwargs.get("timeout", DEFAULT_TIMEOUT))
        if not url_part:
            raise ValueError("Parameter 'url_part' is required")
        try:
            WebDriverWait(self.driver, timeout, 0.5).until(EC.url_contains(url_part))
            print(f"[Wait] URL contains '{url_part}': {self.driver.current_url}")
        except TimeoutException:
            raise TimeoutException(f"URL did not contain '{url_part}' within {timeout}s, current: {self.driver.current_url}")
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException, ElementNotInteractableException
from web_base_utils import DEFAULT_TIMEOUT, MAX_RETRIES, RETRY_DELAY, scroll_to_element, safe_find_visible_element, safe_find_elements, safe_click, safe_input, wait_page_ready, dismiss_alerts_and_popups, try_find_with_fallbacks
