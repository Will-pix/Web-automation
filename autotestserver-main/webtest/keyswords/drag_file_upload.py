class drag_file_upload:
    """Simulate drag-and-drop file upload by injecting a hidden file input"""

    def __init__(self, driver):
        self.driver = driver

    def drag_file_upload(self, **kwargs):
        by_type = kwargs.get("by_type", "xpath")
        locator = kwargs.get("locator", "")
        file_path = kwargs.get("file_path", "")
        if not locator or not file_path:
            raise ValueError("Parameters 'locator' and 'file_path' are required")
        import os
        if not os.path.isabs(file_path):
            file_path = os.path.abspath(file_path)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        by_map = {"xpath": By.XPATH, "css": By.CSS_SELECTOR}
        by = by_map.get(by_type.lower(), By.XPATH)
        element = safe_find_visible_element(self.driver, by, locator)
        self.driver.execute_script('var fi=document.createElement("input");fi.type="file";fi.style="display:block;position:fixed;left:0;top:0;z-index:99999";document.body.appendChild(fi);arguments[0].parentNode.insertBefore(fi,arguments[0]);', element)
        inputs = self.driver.find_elements(By.XPATH, "//input[@type='file']")
        if inputs:
            inputs[-1].send_keys(file_path)
            print(f"[FileUpload] File submitted: {file_path}")
        else:
            raise RuntimeError("Failed to inject file input element")
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException, ElementNotInteractableException
from web_base_utils import DEFAULT_TIMEOUT, MAX_RETRIES, RETRY_DELAY, scroll_to_element, safe_find_visible_element, safe_find_elements, safe_click, safe_input, wait_page_ready, dismiss_alerts_and_popups, try_find_with_fallbacks
