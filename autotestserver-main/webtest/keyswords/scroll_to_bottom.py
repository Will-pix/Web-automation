class scroll_to_bottom:
    """Scroll to the bottom of the page"""

    def __init__(self, driver):
        self.driver = driver

    def scroll_to_bottom(self, **kwargs):
        smooth = kwargs.get("smooth", "true")
        behavior = "smooth" if smooth.lower() in ("true", "1", "yes") else "auto"
        self.driver.execute_script(f"window.scrollTo({{left: 0, top: document.body.scrollHeight, behavior: '{behavior}'}});")
        print("[Scroll] Scrolled to bottom")
        time.sleep(0.5)
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException, ElementNotInteractableException
from web_base_utils import DEFAULT_TIMEOUT, MAX_RETRIES, RETRY_DELAY, scroll_to_element, safe_find_visible_element, safe_find_elements, safe_click, safe_input, wait_page_ready, dismiss_alerts_and_popups, try_find_with_fallbacks
