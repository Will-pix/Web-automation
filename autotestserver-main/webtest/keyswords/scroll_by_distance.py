class scroll_by_distance:
    """Scroll page by pixel distance"""

    def __init__(self, driver):
        self.driver = driver

    def scroll_by_distance(self, **kwargs):
        x_dist = int(kwargs.get("x_distance", 0))
        y_dist = int(kwargs.get("y_distance", 0))
        smooth = kwargs.get("smooth", "true")
        behavior = "smooth" if smooth.lower() in ("true", "1", "yes") else "auto"
        self.driver.execute_script(f"window.scrollBy({{left: {x_dist}, top: {y_dist}, behavior: '{behavior}'}});")
        print(f"[Scroll] Scrolled by x:{x_dist} y:{y_dist}")
        time.sleep(0.3)
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException, ElementNotInteractableException
from web_base_utils import DEFAULT_TIMEOUT, MAX_RETRIES, RETRY_DELAY, scroll_to_element, safe_find_visible_element, safe_find_elements, safe_click, safe_input, wait_page_ready, dismiss_alerts_and_popups, try_find_with_fallbacks
