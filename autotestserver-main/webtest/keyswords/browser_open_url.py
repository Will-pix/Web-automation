class browser_open_url:
    """Open URL with page load wait and retry"""

    def __init__(self, driver):
        self.driver = driver

    def browser_open_url(self, **kwargs):
        url = kwargs.get("url", "")
        if not url:
            raise ValueError("Parameter 'url' is required")
        if not url.startswith("http"):
            url = "https://" + url
        for attempt in range(MAX_RETRIES):
            try:
                self.driver.get(url)
                wait_page_ready(self.driver, timeout=30)
                dismiss_alerts_and_popups(self.driver)
                print(f"[Browser] Page opened: {url}")
                return
            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    print(f"[Retry] Open URL failed (attempt {attempt+1}): {e}")
                    time.sleep(2)
                else:
                    raise RuntimeError(f"Failed to open URL after {MAX_RETRIES} retries: {url}")
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException, ElementNotInteractableException
from web_base_utils import DEFAULT_TIMEOUT, MAX_RETRIES, RETRY_DELAY, scroll_to_element, safe_find_visible_element, safe_find_elements, safe_click, safe_input, wait_page_ready, dismiss_alerts_and_popups, try_find_with_fallbacks
