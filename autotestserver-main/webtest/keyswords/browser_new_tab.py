class browser_new_tab:
    """Open a new browser tab and optionally navigate to URL"""

    def __init__(self, driver):
        self.driver = driver

    def browser_new_tab(self, **kwargs):
        url = kwargs.get("url", "")
        old_handles = self.driver.window_handles
        self.driver.execute_script("window.open('');")
        time.sleep(0.5)
        new_handles = self.driver.window_handles
        for h in new_handles:
            if h not in old_handles:
                self.driver.switch_to.window(h)
                break
        print("[Browser] New tab opened")
        if url:
            if not url.startswith("http"):
                url = "https://" + url
            self.driver.get(url)
            wait_page_ready(self.driver)
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException, ElementNotInteractableException
from web_base_utils import DEFAULT_TIMEOUT, MAX_RETRIES, RETRY_DELAY, scroll_to_element, safe_find_visible_element, safe_find_elements, safe_click, safe_input, wait_page_ready, dismiss_alerts_and_popups, try_find_with_fallbacks
