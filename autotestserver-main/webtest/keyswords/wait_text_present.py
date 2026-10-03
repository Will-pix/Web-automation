class wait_text_present:
    """Wait for specific text to appear on the page"""

    def __init__(self, driver):
        self.driver = driver

    def wait_text_present(self, **kwargs):
        text = kwargs.get("text", "")
        timeout = int(kwargs.get("timeout", DEFAULT_TIMEOUT))
        if not text:
            raise ValueError("Parameter 'text' is required")
        try:
            WebDriverWait(self.driver, timeout, 0.5).until(EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{text}')]")))
            print(f"[Wait] Text found: '{text}'")
        except TimeoutException:
            raise TimeoutException(f"Text '{text}' did not appear within {timeout}s")
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException, ElementNotInteractableException
from web_base_utils import DEFAULT_TIMEOUT, MAX_RETRIES, RETRY_DELAY, scroll_to_element, safe_find_visible_element, safe_find_elements, safe_click, safe_input, wait_page_ready, dismiss_alerts_and_popups, try_find_with_fallbacks
