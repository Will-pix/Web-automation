class element_select_dropdown:
    """Select dropdown option - supports native <select> and UI framework dropdowns"""

    def __init__(self, driver):
        self.driver = driver

    def element_select_dropdown(self, **kwargs):
        by_type = kwargs.get("by_type", "xpath")
        locator = kwargs.get("locator", "")
        option_text = kwargs.get("option_text", "")
        option_value = kwargs.get("option_value", "")
        if not locator:
            raise ValueError("Parameter 'locator' is required")
        by_map = {"xpath": By.XPATH, "id": By.ID, "name": By.NAME, "css selector": By.CSS_SELECTOR, "css": By.CSS_SELECTOR}
        by = by_map.get(by_type.lower(), By.XPATH)
        for attempt in range(MAX_RETRIES):
            try:
                element = safe_find_visible_element(self.driver, by, locator)
                scroll_to_element(self.driver, element)
                if element.tag_name.lower() == "select":
                    from selenium.webdriver.support.ui import Select
                    sel = Select(element)
                    if option_text:
                        sel.select_by_visible_text(option_text)
                    elif option_value:
                        sel.select_by_value(option_value)
                    print(f"[Select] Native select: {option_text or option_value}")
                else:
                    safe_click(self.driver, element)
                    time.sleep(0.5)
                    if option_text:
                        opt_xpath = f"//*[contains(@class,'option') or contains(@class,'item') or contains(@class,'select-dropdown')]//*[contains(text(),'{option_text}')]"
                        try:
                            opt = safe_find_visible_element(self.driver, By.XPATH, opt_xpath, timeout=5)
                            safe_click(self.driver, opt)
                        except Exception:
                            from selenium.webdriver.common.keys import Keys
                            element.send_keys(option_text)
                            time.sleep(0.3)
                            element.send_keys(Keys.ENTER)
                    print(f"[Select] Selected: {option_text or option_value}")
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
