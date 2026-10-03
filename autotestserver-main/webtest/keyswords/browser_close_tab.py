class browser_close_tab:
    """Close current tab and switch to the last remaining tab"""

    def __init__(self, driver):
        self.driver = driver

    def browser_close_tab(self, **kwargs):
        handles = self.driver.window_handles
        if len(handles) <= 1:
            print("[Browser] Only one tab, not closing")
            return
        current = self.driver.current_window_handle
        self.driver.close()
        time.sleep(0.3)
        remaining = self.driver.window_handles
        self.driver.switch_to.window(remaining[-1])
        print(f"[Browser] Closed tab, now on: {self.driver.title}")
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException, ElementNotInteractableException
from web_base_utils import DEFAULT_TIMEOUT, MAX_RETRIES, RETRY_DELAY, scroll_to_element, safe_find_visible_element, safe_find_elements, safe_click, safe_input, wait_page_ready, dismiss_alerts_and_popups, try_find_with_fallbacks
