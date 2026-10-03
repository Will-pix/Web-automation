class element_smart_input:
    """Robust text input with clear, verify, JS fallback and fake-input support"""

    def __init__(self, driver):
        self.driver = driver

    def element_smart_input(self, **kwargs):
        by_type = kwargs.get("by_type", "xpath")
        locator = kwargs.get("locator", "")
        text = kwargs.get("text", "")
        need_clear = kwargs.get("need_clear", "true")
        need_enter = kwargs.get("need_enter", "false")
        clear_first = need_clear.lower() in ("true", "1", "yes")
        press_enter = need_enter.lower() in ("true", "1", "yes")
        if not locator:
            raise ValueError("Parameter 'locator' is required")
        by_map = {"xpath": By.XPATH, "id": By.ID, "name": By.NAME, "css selector": By.CSS_SELECTOR, "css": By.CSS_SELECTOR, "class name": By.CLASS_NAME, "tag name": By.TAG_NAME}
        by = by_map.get(by_type.lower(), By.XPATH)
        for attempt in range(MAX_RETRIES):
            try:
                element = safe_find_visible_element(self.driver, by, locator)
                scroll_to_element(self.driver, element)
                time.sleep(0.3)
                if element.tag_name.lower() not in ['input', 'textarea']:
                    element.click()
                    time.sleep(0.5)
                    try:
                        active = self.driver.switch_to.active_element
                        if active and active.tag_name.lower() in ['input', 'textarea']:
                            element = active
                    except Exception:
                        pass
                try:
                    element.click()
                except Exception:
                    self.driver.execute_script("arguments[0].click();", element)
                time.sleep(0.2)
                if clear_first:
                    try:
                        element.clear()
                    except Exception:
                        pass
                    from selenium.webdriver.common.keys import Keys
                    element.send_keys(Keys.CONTROL, "a")
                    element.send_keys(Keys.BACKSPACE)
                element.send_keys(text)
                if press_enter:
                    from selenium.webdriver.common.keys import Keys
                    element.send_keys(Keys.ENTER)
                time.sleep(0.3)
                if element.tag_name.lower() in ['input', 'textarea']:
                    val = element.get_attribute("value") or ""
                    if val != text and text not in val:
                        self.driver.execute_script("arguments[0].value=arguments[1];arguments[0].dispatchEvent(new Event('input',{bubbles:true}));arguments[0].dispatchEvent(new Event('change',{bubbles:true}));", element, text)
                else:
                    self.driver.execute_script("arguments[0].dispatchEvent(new Event('input',{bubbles:true}));", element)
                print(f"[Input] Text entered: '{text}'")
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
