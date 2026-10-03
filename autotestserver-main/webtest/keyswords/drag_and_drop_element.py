class drag_and_drop_element:
    """Drag element A and drop onto element B"""

    def __init__(self, driver):
        self.driver = driver

    def drag_and_drop_element(self, **kwargs):
        s_by_type = kwargs.get("source_by_type", "xpath")
        s_locator = kwargs.get("source_locator", "")
        t_by_type = kwargs.get("target_by_type", "xpath")
        t_locator = kwargs.get("target_locator", "")
        if not s_locator or not t_locator:
            raise ValueError("Parameters 'source_locator' and 'target_locator' are required")
        by_map = {"xpath": By.XPATH, "id": By.ID, "name": By.NAME, "css selector": By.CSS_SELECTOR, "css": By.CSS_SELECTOR}
        s_by = by_map.get(s_by_type.lower(), By.XPATH)
        t_by = by_map.get(t_by_type.lower(), By.XPATH)
        for attempt in range(MAX_RETRIES):
            try:
                source = safe_find_visible_element(self.driver, s_by, s_locator)
                target = safe_find_visible_element(self.driver, t_by, t_locator)
                scroll_to_element(self.driver, source)
                time.sleep(0.3)
                try:
                    from selenium.webdriver.common.action_chains import ActionChains
                    ActionChains(self.driver).drag_and_drop(source, target).perform()
                    print("[Drag] ActionChains drag and drop OK")
                except Exception:
                    self.driver.execute_script('function dnd(s,t){var e=["dragstart","drag","dragenter","dragover","drop","dragend"];e.forEach(function(n){var ev=new Event(n,{bubbles:true,cancelable:true});ev.dataTransfer=new DataTransfer();if(n.startsWith("drag"))s.dispatchEvent(ev);else t.dispatchEvent(ev);});}dnd(arguments[0],arguments[1]);', source, target)
                    print("[Drag] JS drag and drop fallback OK")
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
