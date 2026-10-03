class browser_close_all_popups:
    """Close all popup tabs and return to main window"""

    def __init__(self, driver):
        self.driver = driver

    def browser_close_all_popups(self, **kwargs):
        handles = self.driver.window_handles
        main = handles[0]
        for h in handles:
            if h != main:
                self.driver.switch_to.window(h)
                self.driver.close()
        self.driver.switch_to.window(main)
        print("[Browser] All popup tabs closed")
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException, ElementNotInteractableException
from web_base_utils import DEFAULT_TIMEOUT, MAX_RETRIES, RETRY_DELAY, scroll_to_element, safe_find_visible_element, safe_find_elements, safe_click, safe_input, wait_page_ready, dismiss_alerts_and_popups, try_find_with_fallbacks
