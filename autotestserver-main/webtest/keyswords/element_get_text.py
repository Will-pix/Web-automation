class element_get_text:
    """Get element text and store in global variable"""

    def __init__(self, driver):
        self.driver = driver

    def element_get_text(self, **kwargs):
        by_type = kwargs.get("by_type", "xpath")
        locator = kwargs.get("locator", "")
        var_name = kwargs.get("var_name", "text_result")
        if not locator or not var_name:
            raise ValueError("Parameters 'locator' and 'var_name' are required")
        by_map = {"xpath": By.XPATH, "id": By.ID, "name": By.NAME, "css selector": By.CSS_SELECTOR, "css": By.CSS_SELECTOR, "class name": By.CLASS_NAME, "tag name": By.TAG_NAME}
        by = by_map.get(by_type.lower(), By.XPATH)
        for attempt in range(MAX_RETRIES):
            try:
                element = safe_find_visible_element(self.driver, by, locator)
                scroll_to_element(self.driver, element)
                text = element.text.strip()
                from webtest.tool.webrun.core.globalContext import g_context
                g_context().set_dict(var_name, text)
                print(f"[GetText] '{var_name}' = '{text}'")
                return
            except StaleElementReferenceException:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                raise
            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                else:
                    raise
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException, ElementNotInteractableException
from web_base_utils import DEFAULT_TIMEOUT, MAX_RETRIES, RETRY_DELAY, scroll_to_element, safe_find_visible_element, safe_find_elements, safe_click, safe_input, wait_page_ready, dismiss_alerts_and_popups, try_find_with_fallbacks
