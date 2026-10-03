class generic_form_login:
    """Generic form login with auto-detection of common login fields"""

    def __init__(self, driver):
        self.driver = driver

    def generic_form_login(self, **kwargs):
        username = kwargs.get("username", "")
        password = kwargs.get("password", "")
        if not username or not password:
            raise ValueError("Parameters 'username' and 'password' are required")
        by_map = {"xpath": By.XPATH, "id": By.ID, "name": By.NAME, "css selector": By.CSS_SELECTOR, "css": By.CSS_SELECTOR}
        # Find username input
        ub = kwargs.get("username_by_type", "")
        ul = kwargs.get("username_locator", "")
        if ub and ul:
            user_elem = safe_find_visible_element(self.driver, by_map.get(ub.lower(), By.XPATH), ul)
        else:
            user_elem = self._find_input(['username','account','user','email','phone'], ['用户名','账号','手机','邮箱','Username','Email'])
        scroll_to_element(self.driver, user_elem)
        user_elem.clear()
        user_elem.send_keys(username)
        time.sleep(0.3)
        # Find password input
        pb = kwargs.get("password_by_type", "")
        pl = kwargs.get("password_locator", "")
        if pb and pl:
            pass_elem = safe_find_visible_element(self.driver, by_map.get(pb.lower(), By.XPATH), pl)
        else:
            pass_elem = self._find_password_input()
        scroll_to_element(self.driver, pass_elem)
        pass_elem.clear()
        pass_elem.send_keys(password)
        time.sleep(0.3)
        # Find and click login button
        lb = kwargs.get("login_btn_by_type", "")
        ll = kwargs.get("login_btn_locator", "")
        if lb and ll:
            btn = safe_find_visible_element(self.driver, by_map.get(lb.lower(), By.XPATH), ll)
        else:
            btn = self._find_login_button()
        safe_click(self.driver, btn)
        wait_page_ready(self.driver, timeout=15)
        dismiss_alerts_and_popups(self.driver)
        print(f"[Login] Login flow completed, current URL: {self.driver.current_url}")

    def _find_input(self, name_ids, placeholders):
        for nid in name_ids:
            try:
                return safe_find_visible_element(self.driver, By.XPATH, f"//input[@name='{nid}' or @id='{nid}']", timeout=3)
            except Exception:
                continue
        for ph in placeholders:
            try:
                return safe_find_visible_element(self.driver, By.XPATH, f"//input[contains(@placeholder,'{ph}')]", timeout=3)
            except Exception:
                continue
        return safe_find_visible_element(self.driver, By.XPATH, "//input[@type='text'][1]")

    def _find_password_input(self):
        return safe_find_visible_element(self.driver, By.XPATH, "//input[@type='password'][1]")

    def _find_login_button(self):
        for text in ['登录','Sign in','Login']:
            try:
                return safe_find_visible_element(self.driver, By.XPATH, f"//button[contains(text(),'{text}')]", timeout=3)
            except Exception:
                continue
        try:
            return safe_find_visible_element(self.driver, By.XPATH, "//*[@type='submit']", timeout=3)
        except Exception:
            return safe_find_visible_element(self.driver, By.XPATH, "//button[1]")
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException, ElementNotInteractableException
from web_base_utils import DEFAULT_TIMEOUT, MAX_RETRIES, RETRY_DELAY, scroll_to_element, safe_find_visible_element, safe_find_elements, safe_click, safe_input, wait_page_ready, dismiss_alerts_and_popups, try_find_with_fallbacks
