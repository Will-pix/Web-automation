class browser_switch_tab:
    """Switch between browser tabs by index or title"""

    def __init__(self, driver):
        self.driver = driver

    def browser_switch_tab(self, **kwargs):
        tab_index = kwargs.get("tab_index", "")
        tab_title = kwargs.get("tab_title", "")
        handles = self.driver.window_handles
        if tab_title:
            current = self.driver.current_window_handle
            for h in handles:
                self.driver.switch_to.window(h)
                if tab_title in self.driver.title:
                    print(f"[Browser] Switched to tab: {self.driver.title}")
                    return
            self.driver.switch_to.window(current)
            raise RuntimeError(f"Tab with title containing '{tab_title}' not found")
        else:
            idx = int(tab_index) if tab_index else 0
            if idx < 0:
                idx = len(handles) + idx
            if idx >= len(handles):
                raise IndexError(f"Tab index {idx} out of range (total {len(handles)})")
            self.driver.switch_to.window(handles[idx])
            print(f"[Browser] Switched to tab {idx}: {self.driver.title}")
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException, ElementNotInteractableException
from web_base_utils import DEFAULT_TIMEOUT, MAX_RETRIES, RETRY_DELAY, scroll_to_element, safe_find_visible_element, safe_find_elements, safe_click, safe_input, wait_page_ready, dismiss_alerts_and_popups, try_find_with_fallbacks
