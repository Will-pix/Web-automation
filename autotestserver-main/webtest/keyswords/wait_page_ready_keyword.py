class wait_page_ready_keyword:
    """Wait for page to be fully loaded (document.readyState === 'complete')"""

    def __init__(self, driver):
        self.driver = driver

    def wait_page_ready_keyword(self, **kwargs):
        timeout = int(kwargs.get("timeout", 30))
        wait_page_ready(self.driver, timeout=timeout)
        print("[Wait] Page ready")
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException, ElementNotInteractableException
from web_base_utils import DEFAULT_TIMEOUT, MAX_RETRIES, RETRY_DELAY, scroll_to_element, safe_find_visible_element, safe_find_elements, safe_click, safe_input, wait_page_ready, dismiss_alerts_and_popups, try_find_with_fallbacks
