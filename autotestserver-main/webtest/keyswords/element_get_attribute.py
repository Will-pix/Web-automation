class element_get_attribute:
    """Get element attribute value and store in global variable"""

    def __init__(self, driver):
        self.driver = driver

    def element_get_attribute(self, **kwargs):
        by_type = kwargs.get("by_type", "xpath")
        locator = kwargs.get("locator", "")
        attr_name = kwargs.get("attr_name", "value")
        var_name = kwargs.get("var_name", "attr_result")
        if not locator:
            raise ValueError("Parameter 'locator' is required")
        by_map = {"xpath": By.XPATH, "id": By.ID, "name": By.NAME, "css selector": By.CSS_SELECTOR, "css": By.CSS_SELECTOR, "class name": By.CLASS_NAME}
        by = by_map.get(by_type.lower(), By.XPATH)
        for attempt in range(MAX_RETRIES):
            try:
                element = safe_find_visible_element(self.driver, by, locator)
                val = element.get_attribute(attr_name)
                from webtest.tool.webrun.core.globalContext import g_context
                g_context().set_dict(var_name, val)
                print(f"[GetAttr] '{var_name}' = '{val}'")
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
