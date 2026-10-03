# -*- coding: UTF-8 -*-
"""
修复所有关键字：
1. 删除旧的多class文件，创建独立的单class .py文件
2. 更新数据库 keyword_value (代码体) 和 keyword_desc (英文参数名)
3. 确保 file_name = class_name = method_name
"""
import os
import json
import pymysql
from datetime import datetime

KEYWORDS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'webtest', 'keyswords')

# 需要删除的多class文件
OLD_FILES = [
    'browser_open_url.py', 'wait_element_visible.py', 'element_get_text.py',
    'scroll_by_distance.py', 'assert_text_present.py', 'drag_and_drop_element.py',
    'coordinate_smart_click.py', 'api_get_request.py', 'file_wait_download.py',
    'element_smart_click.py', 'element_smart_input.py', 'generic_form_login.py',
]

# 删除旧文件
for fname in OLD_FILES:
    fpath = os.path.join(KEYWORDS_DIR, fname)
    if os.path.exists(fpath):
        os.remove(fpath)
        print(f'[删除] {fname}')

# 通用导入模板 (放在文件底部，与现有模式一致)
COMMON_IMPORTS = """
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException, ElementNotInteractableException
from web_base_utils import DEFAULT_TIMEOUT, MAX_RETRIES, RETRY_DELAY, scroll_to_element, safe_find_visible_element, safe_find_elements, safe_click, safe_input, wait_page_ready, dismiss_alerts_and_popups, try_find_with_fallbacks
"""

IMPORTS_WITH_ACTIONS = COMMON_IMPORTS + """
from selenium.webdriver.common.action_chains import ActionChains
"""

IMPORTS_WITH_KEYS = COMMON_IMPORTS + """
from selenium.webdriver.common.keys import Keys
"""

IMPORTS_WITH_CONTEXT = COMMON_IMPORTS + """
from webtest.tool.webrun.core.globalContext import g_context
"""

IMPORTS_WITH_CONTEXT_RENDER = COMMON_IMPORTS + """
from webtest.tool.webrun.core.globalContext import g_context
from webtest.tool.webrun.utils.VarRender import refresh
"""

IMPORTS_WITH_REQUESTS = COMMON_IMPORTS + """
import requests
import json as json_mod
from webtest.tool.webrun.core.globalContext import g_context
from webtest.tool.webrun.utils.VarRender import refresh
"""


def write_keyword_file(fun_name, code_body):
    """写入单个关键字 .py 文件"""
    fpath = os.path.join(KEYWORDS_DIR, f'{fun_name}.py')
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(code_body)
    print(f'  [FILE] {fun_name}.py')


def update_db(fun_name, code_body, desc_json):
    """更新数据库记录"""
    cursor.execute(
        'UPDATE t_web_keyword SET keyword_value = %s, keyword_desc = %s WHERE keyword_fun_name = %s',
        (code_body, desc_json, fun_name)
    )
    return cursor.rowcount


# 定义所有关键字： (name, fun_name, op_type_id, param_list, code_body)
# param_list: [(english_name, placeholder), ...]

keywords_data = []

# ==================== 浏览器操作 (op_type=1) ====================

keywords_data.append(('打开URL', 'browser_open_url', 1,
    [('url', 'URL to open (http prefix can be omitted)')],
    '''class browser_open_url:
    """Open URL with page load wait and retry"""

    def __init__(self, driver):
        self.driver = driver

    def browser_open_url(self, **kwargs):
        url = kwargs.get("url", "")
        if not url:
            raise ValueError("Parameter 'url' is required")
        if not url.startswith("http"):
            url = "https://" + url
        for attempt in range(MAX_RETRIES):
            try:
                self.driver.get(url)
                wait_page_ready(self.driver, timeout=30)
                dismiss_alerts_and_popups(self.driver)
                print(f"[Browser] Page opened: {url}")
                return
            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    print(f"[Retry] Open URL failed (attempt {attempt+1}): {e}")
                    time.sleep(2)
                else:
                    raise RuntimeError(f"Failed to open URL after {MAX_RETRIES} retries: {url}")''' + COMMON_IMPORTS
))

keywords_data.append(('打开新标签页', 'browser_new_tab', 1,
    [('url', 'URL to load in new tab (optional)')],
    '''class browser_new_tab:
    """Open a new browser tab and optionally navigate to URL"""

    def __init__(self, driver):
        self.driver = driver

    def browser_new_tab(self, **kwargs):
        url = kwargs.get("url", "")
        old_handles = self.driver.window_handles
        self.driver.execute_script("window.open('');")
        time.sleep(0.5)
        new_handles = self.driver.window_handles
        for h in new_handles:
            if h not in old_handles:
                self.driver.switch_to.window(h)
                break
        print("[Browser] New tab opened")
        if url:
            if not url.startswith("http"):
                url = "https://" + url
            self.driver.get(url)
            wait_page_ready(self.driver)''' + COMMON_IMPORTS
))

keywords_data.append(('切换标签页', 'browser_switch_tab', 1,
    [('tab_index', 'Tab index (0-based, default 0)'),
     ('tab_title', 'Tab title to match (alternative to index)')],
    '''class browser_switch_tab:
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
            print(f"[Browser] Switched to tab {idx}: {self.driver.title}")''' + COMMON_IMPORTS
))

keywords_data.append(('关闭标签页', 'browser_close_tab', 1, [],
    '''class browser_close_tab:
    """Close current tab and switch to the last remaining tab"""

    def __init__(self, driver):
        self.driver = driver

    def browser_close_tab(self, **kwargs):
        handles = self.driver.window_handles
        if len(handles) <= 1:
            print("[Browser] Only one tab, not closing")
            return
        current = self.driver.current_window_handle
        self.driver.close()
        time.sleep(0.3)
        remaining = self.driver.window_handles
        self.driver.switch_to.window(remaining[-1])
        print(f"[Browser] Closed tab, now on: {self.driver.title}")''' + COMMON_IMPORTS
))

keywords_data.append(('刷新页面', 'browser_refresh', 1, [],
    '''class browser_refresh:
    """Refresh current page and wait for load"""

    def __init__(self, driver):
        self.driver = driver

    def browser_refresh(self, **kwargs):
        self.driver.refresh()
        wait_page_ready(self.driver)
        dismiss_alerts_and_popups(self.driver)
        print("[Browser] Page refreshed")''' + COMMON_IMPORTS
))

keywords_data.append(('浏览器后退', 'browser_back', 1, [],
    '''class browser_back:
    """Navigate back in browser history"""

    def __init__(self, driver):
        self.driver = driver

    def browser_back(self, **kwargs):
        self.driver.back()
        wait_page_ready(self.driver)
        print("[Browser] Navigated back")''' + COMMON_IMPORTS
))

keywords_data.append(('浏览器前进', 'browser_forward', 1, [],
    '''class browser_forward:
    """Navigate forward in browser history"""

    def __init__(self, driver):
        self.driver = driver

    def browser_forward(self, **kwargs):
        self.driver.forward()
        wait_page_ready(self.driver)
        print("[Browser] Navigated forward")''' + COMMON_IMPORTS
))

keywords_data.append(('最大化窗口', 'browser_maximize', 1, [],
    '''class browser_maximize:
    """Maximize browser window"""

    def __init__(self, driver):
        self.driver = driver

    def browser_maximize(self, **kwargs):
        self.driver.maximize_window()
        print("[Browser] Window maximized")''' + COMMON_IMPORTS
))

keywords_data.append(('关闭所有弹窗', 'browser_close_all_popups', 1, [],
    '''class browser_close_all_popups:
    """Close all popup tabs and return to main window"""

    def __init__(self, driver):
        self.driver = driver

    def browser_close_all_popups(self, **kwargs):
        handles = self.driver.window_handles
        main = handles[0]
        for h in handles:
            if h != main:
                self.driver.switch_to.window(h)
                self.driver.close()
        self.driver.switch_to.window(main)
        print("[Browser] All popup tabs closed")''' + COMMON_IMPORTS
))

# ==================== 元素操作 (op_type=2) ====================

keywords_data.append(('智能点击', 'element_smart_click', 2,
    [('by_type', 'Locator type: xpath/id/css selector/name/class name/tag name/link text/partial link text'),
     ('locator', 'Element locator value'),
     ('timeout', 'Wait timeout in seconds (default 30)')],
    '''class element_smart_click:
    """Robust element click with retry, scroll, overlay handling and JS fallback"""

    def __init__(self, driver):
        self.driver = driver

    def element_smart_click(self, **kwargs):
        by_type = kwargs.get("by_type", "xpath")
        locator = kwargs.get("locator", "")
        timeout = int(kwargs.get("timeout", DEFAULT_TIMEOUT))
        if not locator:
            raise ValueError("Parameter 'locator' is required")
        by_map = {"xpath": By.XPATH, "id": By.ID, "name": By.NAME, "css selector": By.CSS_SELECTOR, "css": By.CSS_SELECTOR, "class name": By.CLASS_NAME, "tag name": By.TAG_NAME, "link text": By.LINK_TEXT, "partial link text": By.PARTIAL_LINK_TEXT}
        by = by_map.get(by_type.lower(), By.XPATH)
        for attempt in range(MAX_RETRIES):
            try:
                element = safe_find_visible_element(self.driver, by, locator, timeout=timeout)
                scroll_to_element(self.driver, element)
                time.sleep(0.3)
                try:
                    element.click()
                    print(f"[Click] Clicked: {by_type}={locator}")
                except (ElementClickInterceptedException, ElementNotInteractableException):
                    self.driver.execute_script("var o=document.querySelectorAll('.el-overlay,.el-dialog__wrapper,.modal-backdrop,.el-loading-mask,.v-modal');o.forEach(function(e){e.style.display='none';});")
                    time.sleep(0.3)
                    try:
                        element.click()
                    except Exception:
                        self.driver.execute_script("arguments[0].click();", element)
                        print("[Click] JS click fallback")
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
                    raise''' + COMMON_IMPORTS
))

keywords_data.append(('智能输入', 'element_smart_input', 2,
    [('by_type', 'Locator type: xpath/id/css selector/name/class name/tag name'),
     ('locator', 'Element locator value'),
     ('text', 'Text to input'),
     ('need_clear', 'Clear before input: true/false (default true)'),
     ('need_enter', 'Press Enter after input: true/false (default false)')],
    '''class element_smart_input:
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
                    raise''' + COMMON_IMPORTS
))

keywords_data.append(('获取元素文本', 'element_get_text', 2,
    [('by_type', 'Locator type: xpath/id/css selector/name/class name/tag name'),
     ('locator', 'Element locator value'),
     ('var_name', 'Variable name to store the text')],
    '''class element_get_text:
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
                    raise''' + COMMON_IMPORTS
))

keywords_data.append(('获取元素属性', 'element_get_attribute', 2,
    [('by_type', 'Locator type: xpath/id/css selector/name/class name'),
     ('locator', 'Element locator value'),
     ('attr_name', 'Attribute name, e.g. value/class/href'),
     ('var_name', 'Variable name to store the attribute value')],
    '''class element_get_attribute:
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
                    raise''' + COMMON_IMPORTS
))

keywords_data.append(('下拉选择', 'element_select_dropdown', 2,
    [('by_type', 'Locator type: xpath/id/css selector'),
     ('locator', 'Dropdown element locator'),
     ('option_text', 'Option text to select'),
     ('option_value', 'Option value to select (alternative to text)')],
    '''class element_select_dropdown:
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
                    raise''' + COMMON_IMPORTS
))

keywords_data.append(('悬浮元素', 'element_hover', 2,
    [('by_type', 'Locator type: xpath/id/css selector/name/class name/tag name'),
     ('locator', 'Element locator value')],
    '''class element_hover:
    """Hover mouse over element"""

    def __init__(self, driver):
        self.driver = driver

    def element_hover(self, **kwargs):
        by_type = kwargs.get("by_type", "xpath")
        locator = kwargs.get("locator", "")
        if not locator:
            raise ValueError("Parameter 'locator' is required")
        by_map = {"xpath": By.XPATH, "id": By.ID, "name": By.NAME, "css selector": By.CSS_SELECTOR, "css": By.CSS_SELECTOR, "class name": By.CLASS_NAME, "tag name": By.TAG_NAME}
        by = by_map.get(by_type.lower(), By.XPATH)
        for attempt in range(MAX_RETRIES):
            try:
                element = safe_find_visible_element(self.driver, by, locator)
                scroll_to_element(self.driver, element)
                time.sleep(0.3)
                from selenium.webdriver.common.action_chains import ActionChains
                ActionChains(self.driver).move_to_element(element).perform()
                print(f"[Hover] Hovered: {by_type}={locator}")
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
                    raise''' + COMMON_IMPORTS
))

# ==================== 坐标操作 (op_type=4) ====================
COORD_ANCHOR_JS = """
        self.driver.execute_script('var a=document.createElement(\"div\");a.id=\"__ca__\";a.style=\"position:fixed;left:0;top:0;width:1px;height:1px;z-index:99999;pointer-events:none\";document.body.appendChild(a);')
        anchor = self.driver.find_element(By.ID, '__ca__')
        try:"""

COORD_CLEANUP_JS = """
        finally:
            self.driver.execute_script('var a=document.getElementById(\"__ca__\");if(a)a.remove();')"""

keywords_data.append(('坐标点击', 'coordinate_smart_click', 4,
    [('x', 'X coordinate in pixels'), ('y', 'Y coordinate in pixels'),
     ('click_count', 'Number of clicks (default 1)'), ('interval', 'Interval between clicks in seconds (default 0.2)')],
    f'''class coordinate_smart_click:
    """Click at viewport coordinates using anchor element"""

    def __init__(self, driver):
        self.driver = driver

    def coordinate_smart_click(self, **kwargs):
        x = int(kwargs.get("x", 0))
        y = int(kwargs.get("y", 0))
        click_count = int(kwargs.get("click_count", 1))
        interval = float(kwargs.get("interval", 0.2))
        if x <= 0 or y <= 0:
            raise ValueError("Parameters 'x' and 'y' must be positive"){COORD_ANCHOR_JS}
            from selenium.webdriver.common.action_chains import ActionChains
            for i in range(click_count):
                ActionChains(self.driver).move_to_element_with_offset(anchor, x, y).click().perform()
                if click_count > 1 and i < click_count - 1:
                    time.sleep(interval)
            print(f"[CoordClick] ({{x}}, {{y}}) clicked {{click_count}} time(s)"){COORD_CLEANUP_JS}

import time
from selenium.webdriver.common.by import By
'''
))

keywords_data.append(('坐标悬浮', 'coordinate_smart_hover', 4,
    [('x', 'X coordinate in pixels'), ('y', 'Y coordinate in pixels'),
     ('hover_seconds', 'Hover duration in seconds (default 1)')],
    f'''class coordinate_smart_hover:
    """Hover at viewport coordinates"""

    def __init__(self, driver):
        self.driver = driver

    def coordinate_smart_hover(self, **kwargs):
        x = int(kwargs.get("x", 0))
        y = int(kwargs.get("y", 0))
        hover_seconds = float(kwargs.get("hover_seconds", 1)){COORD_ANCHOR_JS}
            from selenium.webdriver.common.action_chains import ActionChains
            ActionChains(self.driver).move_to_element_with_offset(anchor, x, y).perform()
            time.sleep(hover_seconds)
            print(f"[CoordHover] ({{x}}, {{y}}) for {{hover_seconds}}s"){COORD_CLEANUP_JS}

import time
from selenium.webdriver.common.by import By
'''
))

keywords_data.append(('坐标输入', 'coordinate_smart_input', 4,
    [('x', 'X coordinate in pixels'), ('y', 'Y coordinate in pixels'),
     ('text', 'Text to input after clicking at coordinates')],
    f'''class coordinate_smart_input:
    """Click at coordinates then input text into focused element"""

    def __init__(self, driver):
        self.driver = driver

    def coordinate_smart_input(self, **kwargs):
        x = int(kwargs.get("x", 0))
        y = int(kwargs.get("y", 0))
        text = kwargs.get("text", ""){COORD_ANCHOR_JS}
            from selenium.webdriver.common.action_chains import ActionChains
            from selenium.webdriver.common.keys import Keys
            ActionChains(self.driver).move_to_element_with_offset(anchor, x, y).click().perform()
            time.sleep(0.3)
            active = self.driver.switch_to.active_element
            if active and active != self.driver.find_element(By.TAG_NAME, "body"):
                active.send_keys(Keys.CONTROL, "a")
                active.send_keys(Keys.BACKSPACE)
                active.send_keys(text)
                print(f"[CoordInput] Typed: '{{text}}'")
            else:
                print("[CoordInput] Warning: no active input element at coordinates"){COORD_CLEANUP_JS}

import time
from selenium.webdriver.common.by import By
'''
))

keywords_data.append(('坐标双击', 'coordinate_double_click', 4,
    [('x', 'X coordinate in pixels'), ('y', 'Y coordinate in pixels')],
    f'''class coordinate_double_click:
    """Double click at viewport coordinates"""

    def __init__(self, driver):
        self.driver = driver

    def coordinate_double_click(self, **kwargs):
        x = int(kwargs.get("x", 0))
        y = int(kwargs.get("y", 0)){COORD_ANCHOR_JS}
            from selenium.webdriver.common.action_chains import ActionChains
            ActionChains(self.driver).move_to_element_with_offset(anchor, x, y).double_click().perform()
            print(f"[CoordDblClick] ({{x}}, {{y}})"){COORD_CLEANUP_JS}

from selenium.webdriver.common.by import By
'''
))

keywords_data.append(('坐标右键', 'coordinate_right_click', 4,
    [('x', 'X coordinate in pixels'), ('y', 'Y coordinate in pixels')],
    f'''class coordinate_right_click:
    """Right click at viewport coordinates"""

    def __init__(self, driver):
        self.driver = driver

    def coordinate_right_click(self, **kwargs):
        x = int(kwargs.get("x", 0))
        y = int(kwargs.get("y", 0)){COORD_ANCHOR_JS}
            from selenium.webdriver.common.action_chains import ActionChains
            ActionChains(self.driver).move_to_element_with_offset(anchor, x, y).context_click().perform()
            print(f"[CoordRightClick] ({{x}}, {{y}})"){COORD_CLEANUP_JS}

from selenium.webdriver.common.by import By
'''
))

# ==================== 滑动操作 (op_type=5) ====================

keywords_data.append(('滚动到元素', 'scroll_to_element_keyword', 5,
    [('by_type', 'Locator type: xpath/id/css selector'),
     ('locator', 'Element locator value'),
     ('block', 'Scroll alignment: start/center/end (default center)')],
    '''class scroll_to_element_keyword:
    """Scroll element into view"""

    def __init__(self, driver):
        self.driver = driver

    def scroll_to_element_keyword(self, **kwargs):
        by_type = kwargs.get("by_type", "xpath")
        locator = kwargs.get("locator", "")
        block = kwargs.get("block", "center")
        if not locator:
            raise ValueError("Parameter 'locator' is required")
        by_map = {"xpath": By.XPATH, "id": By.ID, "css selector": By.CSS_SELECTOR, "css": By.CSS_SELECTOR, "class name": By.CLASS_NAME, "name": By.NAME}
        by = by_map.get(by_type.lower(), By.XPATH)
        element = safe_find_visible_element(self.driver, by, locator)
        scroll_to_element(self.driver, element, block=block)
        print(f"[Scroll] Scrolled to element: {by_type}={locator}")''' + COMMON_IMPORTS
))

keywords_data.append(('按距离滚动', 'scroll_by_distance', 5,
    [('x_distance', 'Horizontal scroll pixels (default 0)'),
     ('y_distance', 'Vertical scroll pixels (default 0)'),
     ('smooth', 'Smooth scroll: true/false (default true)')],
    '''class scroll_by_distance:
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
        time.sleep(0.3)''' + COMMON_IMPORTS
))

keywords_data.append(('滚动到底部', 'scroll_to_bottom', 5,
    [('smooth', 'Smooth scroll: true/false (default true)')],
    '''class scroll_to_bottom:
    """Scroll to the bottom of the page"""

    def __init__(self, driver):
        self.driver = driver

    def scroll_to_bottom(self, **kwargs):
        smooth = kwargs.get("smooth", "true")
        behavior = "smooth" if smooth.lower() in ("true", "1", "yes") else "auto"
        self.driver.execute_script(f"window.scrollTo({{left: 0, top: document.body.scrollHeight, behavior: '{behavior}'}});")
        print("[Scroll] Scrolled to bottom")
        time.sleep(0.5)''' + COMMON_IMPORTS
))

keywords_data.append(('滚动到顶部', 'scroll_to_top', 5,
    [('smooth', 'Smooth scroll: true/false (default true)')],
    '''class scroll_to_top:
    """Scroll to the top of the page"""

    def __init__(self, driver):
        self.driver = driver

    def scroll_to_top(self, **kwargs):
        smooth = kwargs.get("smooth", "true")
        behavior = "smooth" if smooth.lower() in ("true", "1", "yes") else "auto"
        self.driver.execute_script(f"window.scrollTo({{left: 0, top: 0, behavior: '{behavior}'}});")
        print("[Scroll] Scrolled to top")
        time.sleep(0.5)''' + COMMON_IMPORTS
))

keywords_data.append(('元素内滚动', 'scroll_in_element', 5,
    [('by_type', 'Locator type: xpath/css selector'),
     ('locator', 'Container element locator'),
     ('x_distance', 'Horizontal scroll inside element (default 0)'),
     ('y_distance', 'Vertical scroll inside element (default 100)')],
    '''class scroll_in_element:
    """Scroll inside a specific element"""

    def __init__(self, driver):
        self.driver = driver

    def scroll_in_element(self, **kwargs):
        by_type = kwargs.get("by_type", "xpath")
        locator = kwargs.get("locator", "")
        x_dist = int(kwargs.get("x_distance", 0))
        y_dist = int(kwargs.get("y_distance", 100))
        if not locator:
            raise ValueError("Parameter 'locator' is required")
        by_map = {"xpath": By.XPATH, "css": By.CSS_SELECTOR, "id": By.ID}
        by = by_map.get(by_type.lower(), By.XPATH)
        element = safe_find_visible_element(self.driver, by, locator)
        self.driver.execute_script(f"arguments[0].scrollBy({{left: {x_dist}, top: {y_dist}, behavior: 'smooth'}});", element)
        print(f"[Scroll] Inside element scrolled x:{x_dist} y:{y_dist}")''' + COMMON_IMPORTS
))

keywords_data.append(('屏幕滑动', 'swipe_screen', 5,
    [('start_x', 'Start X coordinate (default 500)'),
     ('start_y', 'Start Y coordinate (default 500)'),
     ('end_x', 'End X coordinate (default 500)'),
     ('end_y', 'End Y coordinate (default 100)'),
     ('duration_ms', 'Swipe duration in ms (default 500)')],
    '''class swipe_screen:
    """Simulate finger swipe on screen (works on PC too)"""

    def __init__(self, driver):
        self.driver = driver

    def swipe_screen(self, **kwargs):
        from selenium.webdriver.common.action_chains import ActionChains
        start_x = int(kwargs.get("start_x", 500))
        start_y = int(kwargs.get("start_y", 500))
        end_x = int(kwargs.get("end_x", 500))
        end_y = int(kwargs.get("end_y", 100))
        duration_ms = int(kwargs.get("duration_ms", 500))
        ActionChains(self.driver).move_by_offset(start_x, start_y).click_and_hold().move_by_offset(end_x - start_x, end_y - start_y).pause(duration_ms / 1000.0).release().perform()
        ActionChains(self.driver).move_by_offset(-end_x, -end_y).perform()
        print(f"[Swipe] From ({start_x},{start_y}) to ({end_x},{end_y})")'''
))

# ==================== API请求操作 (op_type=6) ====================

keywords_data.append(('GET请求', 'api_get_request', 6,
    [('url', 'Request URL'), ('var_name', 'Variable name to store response'),
     ('headers', 'Request headers JSON string (default empty object)')],
    '''class api_get_request:
    """Send HTTP GET request and store response in variable"""

    def __init__(self, driver):
        self.driver = driver

    def api_get_request(self, **kwargs):
        import requests
        import json as json_mod
        url = kwargs.get("url", "")
        var_name = kwargs.get("var_name", "api_response")
        headers_str = kwargs.get("headers", "{}")
        if not url:
            raise ValueError("Parameter 'url' is required")
        from webtest.tool.webrun.core.globalContext import g_context
        from webtest.tool.webrun.utils.VarRender import refresh
        all_ctx = g_context().show_dict()
        url = refresh(url, all_ctx)
        try:
            headers = json_mod.loads(headers_str)
        except Exception:
            headers = {"Content-Type": "application/json"}
        for attempt in range(3):
            try:
                resp = requests.get(url, headers=headers, timeout=30)
                resp.raise_for_status()
                try:
                    data = resp.json()
                except Exception:
                    data = resp.text
                g_context().set_dict(var_name, data)
                print(f"[API] GET {url} -> status={resp.status_code}, stored in '{var_name}'")
                return
            except requests.RequestException as e:
                if attempt < 2:
                    time.sleep(2)
                else:
                    raise RuntimeError(f"API GET failed: {url}, error: {e}")

import time'''
))

keywords_data.append(('POST请求', 'api_post_request', 6,
    [('url', 'Request URL'), ('body', 'Request body JSON string'),
     ('var_name', 'Variable name to store response'),
     ('headers', 'Request headers JSON string')],
    '''class api_post_request:
    """Send HTTP POST request and store response in variable"""

    def __init__(self, driver):
        self.driver = driver

    def api_post_request(self, **kwargs):
        import requests
        import json as json_mod
        url = kwargs.get("url", "")
        body_str = kwargs.get("body", "{}")
        var_name = kwargs.get("var_name", "api_response")
        headers_str = kwargs.get("headers", '{"Content-Type":"application/json"}')
        if not url:
            raise ValueError("Parameter 'url' is required")
        from webtest.tool.webrun.core.globalContext import g_context
        from webtest.tool.webrun.utils.VarRender import refresh
        all_ctx = g_context().show_dict()
        url = refresh(url, all_ctx)
        body_str = refresh(body_str, all_ctx)
        try:
            headers = json_mod.loads(headers_str)
        except Exception:
            headers = {"Content-Type": "application/json"}
        try:
            body = json_mod.loads(body_str)
        except Exception:
            body = body_str
        for attempt in range(3):
            try:
                if isinstance(body, dict):
                    resp = requests.post(url, json=body, headers=headers, timeout=30)
                else:
                    resp = requests.post(url, data=body_str, headers=headers, timeout=30)
                resp.raise_for_status()
                try:
                    data = resp.json()
                except Exception:
                    data = resp.text
                g_context().set_dict(var_name, data)
                print(f"[API] POST {url} -> status={resp.status_code}, stored in '{var_name}'")
                return
            except requests.RequestException as e:
                if attempt < 2:
                    time.sleep(2)
                else:
                    raise RuntimeError(f"API POST failed: {url}, error: {e}")

import time'''
))

keywords_data.append(('提取API响应值', 'api_extract_value', 6,
    [('source_var', 'Variable name containing API response data'),
     ('json_path', 'JSON path, e.g. data.list.0.name'),
     ('target_var', 'Variable name to store extracted value')],
    '''class api_extract_value:
    """Extract value from API response JSON by path and store in variable"""

    def __init__(self, driver):
        self.driver = driver

    def api_extract_value(self, **kwargs):
        source_var = kwargs.get("source_var", "")
        json_path = kwargs.get("json_path", "")
        target_var = kwargs.get("target_var", "extracted")
        if not source_var or not json_path:
            raise ValueError("Parameters 'source_var' and 'json_path' are required")
        from webtest.tool.webrun.core.globalContext import g_context
        data = g_context().get_dict(source_var)
        if data is None:
            raise ValueError(f"Source variable '{source_var}' not found")
        parts = json_path.split(".")
        val = data
        for p in parts:
            try:
                if p.isdigit():
                    val = val[int(p)]
                else:
                    val = val[p]
            except (KeyError, IndexError, TypeError):
                val = None
                break
        g_context().set_dict(target_var, val)
        print(f"[API Extract] {source_var}{json_path} = {val} -> '{target_var}'")'''
))

# ==================== 断言操作 (op_type=7) ====================

keywords_data.append(('断言文本存在', 'assert_text_present', 7,
    [('text', 'Text that should be present on page'),
     ('timeout', 'Wait timeout in seconds (default 30)')],
    '''class assert_text_present:
    """Assert that specified text exists on the page"""

    def __init__(self, driver):
        self.driver = driver

    def assert_text_present(self, **kwargs):
        text = kwargs.get("text", "")
        timeout = int(kwargs.get("timeout", DEFAULT_TIMEOUT))
        if not text:
            raise ValueError("Parameter 'text' is required")
        try:
            xpath = f"//*[contains(text(), '{text}')]"
            WebDriverWait(self.driver, timeout, 0.5).until(EC.presence_of_element_located((By.XPATH, xpath)))
            print(f"[Assert] Text found: '{text}'")
        except TimeoutException:
            body_text = self.driver.find_element(By.TAG_NAME, "body").text[:500]
            raise AssertionError(f"Text '{text}' not found on page. Body (first 500 chars): {body_text}")''' + COMMON_IMPORTS
))

keywords_data.append(('断言元素存在', 'assert_element_exists', 7,
    [('by_type', 'Locator type: xpath/id/css selector/name/class name/tag name'),
     ('locator', 'Element locator value'),
     ('timeout', 'Wait timeout in seconds (default 30)')],
    '''class assert_element_exists:
    """Assert that an element exists in the DOM"""

    def __init__(self, driver):
        self.driver = driver

    def assert_element_exists(self, **kwargs):
        by_type = kwargs.get("by_type", "xpath")
        locator = kwargs.get("locator", "")
        timeout = int(kwargs.get("timeout", DEFAULT_TIMEOUT))
        if not locator:
            raise ValueError("Parameter 'locator' is required")
        by_map = {"xpath": By.XPATH, "id": By.ID, "name": By.NAME, "css selector": By.CSS_SELECTOR, "css": By.CSS_SELECTOR, "class name": By.CLASS_NAME, "tag name": By.TAG_NAME}
        by = by_map.get(by_type.lower(), By.XPATH)
        try:
            WebDriverWait(self.driver, timeout, 0.5).until(EC.presence_of_element_located((by, locator)))
            print(f"[Assert] Element exists: {by_type}={locator}")
        except TimeoutException:
            raise AssertionError(f"Element not found: {by_type}={locator} (timeout {timeout}s)")''' + COMMON_IMPORTS
))

keywords_data.append(('断言元素可见', 'assert_element_visible', 7,
    [('by_type', 'Locator type: xpath/id/css selector/name/class name/tag name'),
     ('locator', 'Element locator value'),
     ('timeout', 'Wait timeout in seconds (default 30)')],
    '''class assert_element_visible:
    """Assert that an element is visible on the page"""

    def __init__(self, driver):
        self.driver = driver

    def assert_element_visible(self, **kwargs):
        by_type = kwargs.get("by_type", "xpath")
        locator = kwargs.get("locator", "")
        timeout = int(kwargs.get("timeout", DEFAULT_TIMEOUT))
        if not locator:
            raise ValueError("Parameter 'locator' is required")
        by_map = {"xpath": By.XPATH, "id": By.ID, "name": By.NAME, "css selector": By.CSS_SELECTOR, "css": By.CSS_SELECTOR, "class name": By.CLASS_NAME, "tag name": By.TAG_NAME}
        by = by_map.get(by_type.lower(), By.XPATH)
        try:
            WebDriverWait(self.driver, timeout, 0.5).until(EC.visibility_of_element_located((by, locator)))
            print(f"[Assert] Element visible: {by_type}={locator}")
        except TimeoutException:
            raise AssertionError(f"Element not visible: {by_type}={locator} (timeout {timeout}s)")''' + COMMON_IMPORTS
))

keywords_data.append(('断言值相等', 'assert_value_equal', 7,
    [('expected', 'Expected value (supports variable references)'),
     ('var_name', 'Variable name to get actual value from'),
     ('actual', 'Direct actual value (alternative to var_name)')],
    '''class assert_value_equal:
    """Assert that two values are equal (supports variable rendering)"""

    def __init__(self, driver):
        self.driver = driver

    def assert_value_equal(self, **kwargs):
        expected = kwargs.get("expected", "")
        var_name = kwargs.get("var_name", "")
        actual = kwargs.get("actual", "")
        from webtest.tool.webrun.core.globalContext import g_context
        from webtest.tool.webrun.utils.VarRender import refresh
        all_ctx = g_context().show_dict()
        if var_name:
            actual = str(g_context().get_dict(var_name))
            actual = refresh(actual, all_ctx)
        elif actual:
            actual = str(actual)
        else:
            raise ValueError("Provide 'var_name' or 'actual' parameter")
        expected = refresh(str(expected), all_ctx)
        if expected.strip() != actual.strip():
            raise AssertionError(f"Value mismatch: expected '{expected}' != actual '{actual}'")
        print(f"[Assert] Values equal: '{expected}'")'''
))

keywords_data.append(('断言元素数量', 'assert_element_count', 7,
    [('by_type', 'Locator type: xpath/css selector/class name'),
     ('locator', 'Element locator value'),
     ('count', 'Expected number of elements'),
     ('operator', 'Comparison: eq/gt/lt/gte/lte (default eq)')],
    '''class assert_element_count:
    """Assert the number of matched elements"""

    def __init__(self, driver):
        self.driver = driver

    def assert_element_count(self, **kwargs):
        by_type = kwargs.get("by_type", "xpath")
        locator = kwargs.get("locator", "")
        expected = int(kwargs.get("count", 1))
        op = kwargs.get("operator", "eq")
        if not locator:
            raise ValueError("Parameter 'locator' is required")
        by_map = {"xpath": By.XPATH, "css": By.CSS_SELECTOR, "class name": By.CLASS_NAME}
        by = by_map.get(by_type.lower(), By.XPATH)
        elements = safe_find_elements(self.driver, by, locator)
        actual = len(elements)
        op_map = {"eq": lambda a, e: a == e, "gt": lambda a, e: a > e, "lt": lambda a, e: a < e, "gte": lambda a, e: a >= e, "lte": lambda a, e: a <= e}
        if not op_map.get(op, op_map["eq"])(actual, expected):
            raise AssertionError(f"Element count mismatch: {actual} {op} {expected}")
        print(f"[Assert] Element count OK: {actual} {op} {expected}")''' + COMMON_IMPORTS
))

# ==================== 文件操作 (op_type=8) ====================

keywords_data.append(('等待文件下载', 'file_wait_download', 8,
    [('download_dir', 'Download directory path'),
     ('filename_pattern', 'Filename glob pattern, e.g. *.xlsx'),
     ('timeout', 'Wait timeout in seconds (default 60)'),
     ('var_name', 'Variable name to store downloaded file path')],
    '''class file_wait_download:
    """Wait for a file to finish downloading by monitoring the download directory"""

    def __init__(self, driver):
        self.driver = driver

    def file_wait_download(self, **kwargs):
        import os
        download_dir = kwargs.get("download_dir", os.path.expanduser("~/Downloads"))
        pattern = kwargs.get("filename_pattern", "*")
        timeout = int(kwargs.get("timeout", 60))
        var_name = kwargs.get("var_name", "downloaded_file")
        if not os.path.exists(download_dir):
            raise FileNotFoundError(f"Download directory not found: {download_dir}")
        before = set(os.listdir(download_dir))
        waited = 0
        while waited < timeout:
            time.sleep(2)
            waited += 2
            after = set(os.listdir(download_dir))
            new_files = after - before
            for f in new_files:
                if f.endswith(('.crdownload', '.tmp', '.part')):
                    continue
                import fnmatch
                if fnmatch.fnmatch(f, pattern):
                    filepath = os.path.join(download_dir, f)
                    time.sleep(1)
                    if os.path.getsize(filepath) > 0:
                        from webtest.tool.webrun.core.globalContext import g_context
                        g_context().set_dict(var_name, filepath)
                        print(f"[File] Download complete: {filepath}")
                        return
        raise TimeoutError(f"Download timeout: {download_dir}/{pattern}")

import time'''
))

keywords_data.append(('文件存在检查', 'file_exists_check', 8,
    [('file_path', 'File path to check'),
     ('var_name', 'Variable name to store result (true/false)')],
    '''class file_exists_check:
    """Check if a file exists and store result in variable"""

    def __init__(self, driver):
        self.driver = driver

    def file_exists_check(self, **kwargs):
        import os
        file_path = kwargs.get("file_path", "")
        var_name = kwargs.get("var_name", "file_exists")
        if not file_path:
            raise ValueError("Parameter 'file_path' is required")
        if not os.path.isabs(file_path):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            from app import application
            upload_dir = application.config.get('UPLOAD_FOLDER', '../file')
            file_path = os.path.abspath(os.path.join(current_dir, upload_dir, file_path))
        exists = os.path.exists(file_path) and os.path.isfile(file_path)
        from webtest.tool.webrun.core.globalContext import g_context
        g_context().set_dict(var_name, "true" if exists else "false")
        print(f"[File] {file_path} exists: {exists}")'''
))

keywords_data.append(('文件清理', 'file_cleanup', 8,
    [('directory', 'Directory to clean up'),
     ('glob_pattern', 'File glob pattern, e.g. *.xlsx (default *)')],
    '''class file_cleanup:
    """Delete files matching pattern in a directory"""

    def __init__(self, driver):
        self.driver = driver

    def file_cleanup(self, **kwargs):
        import os
        import glob as glob_mod
        directory = kwargs.get("directory", "")
        pattern = kwargs.get("glob_pattern", "*")
        if not directory:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            from app import application
            directory = os.path.abspath(os.path.join(current_dir, application.config.get('UPLOAD_FOLDER', '../file')))
        elif not os.path.isabs(directory):
            directory = os.path.abspath(directory)
        if not os.path.exists(directory):
            print(f"[File] Directory not found, skipping: {directory}")
            return
        count = 0
        for f in glob_mod.glob(os.path.join(directory, pattern)):
            if os.path.isfile(f):
                os.remove(f)
                count += 1
        print(f"[File] Cleaned {count} files from {directory}")'''
))

# ==================== 拖拽操作 (op_type=9) ====================

keywords_data.append(('拖拽元素', 'drag_and_drop_element', 9,
    [('source_by_type', 'Source element locator type'),
     ('source_locator', 'Source element locator'),
     ('target_by_type', 'Target element locator type'),
     ('target_locator', 'Target element locator')],
    '''class drag_and_drop_element:
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
                    raise''' + COMMON_IMPORTS
))

keywords_data.append(('按偏移拖拽', 'drag_by_offset', 9,
    [('by_type', 'Locator type: xpath/id/css selector'),
     ('locator', 'Element locator to drag'),
     ('x_offset', 'Horizontal drag offset in pixels'),
     ('y_offset', 'Vertical drag offset in pixels')],
    '''class drag_by_offset:
    """Drag element by pixel offset"""

    def __init__(self, driver):
        self.driver = driver

    def drag_by_offset(self, **kwargs):
        by_type = kwargs.get("by_type", "xpath")
        locator = kwargs.get("locator", "")
        x_offset = int(kwargs.get("x_offset", 0))
        y_offset = int(kwargs.get("y_offset", 0))
        if not locator:
            raise ValueError("Parameter 'locator' is required")
        by_map = {"xpath": By.XPATH, "id": By.ID, "name": By.NAME, "css selector": By.CSS_SELECTOR, "css": By.CSS_SELECTOR}
        by = by_map.get(by_type.lower(), By.XPATH)
        from selenium.webdriver.common.action_chains import ActionChains
        element = safe_find_visible_element(self.driver, by, locator)
        scroll_to_element(self.driver, element)
        ActionChains(self.driver).click_and_hold(element).move_by_offset(x_offset, y_offset).pause(0.3).release().perform()
        print(f"[Drag] Dragged by x:{x_offset} y:{y_offset}")''' + COMMON_IMPORTS
))

keywords_data.append(('拖拽文件上传', 'drag_file_upload', 9,
    [('by_type', 'Locator type: xpath/css selector'),
     ('locator', 'Drop zone element locator'),
     ('file_path', 'Absolute path of file to upload')],
    '''class drag_file_upload:
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
            raise RuntimeError("Failed to inject file input element")''' + COMMON_IMPORTS
))

# ==================== 登录操作 (op_type=10) ====================

keywords_data.append(('通用表单登录', 'generic_form_login', 10,
    [('username', 'Login username'), ('password', 'Login password'),
     ('username_by_type', 'Username field locator type (optional, auto-detect)'),
     ('username_locator', 'Username field locator (optional, auto-detect)'),
     ('password_by_type', 'Password field locator type (optional, auto-detect)'),
     ('password_locator', 'Password field locator (optional, auto-detect)'),
     ('login_btn_by_type', 'Login button locator type (optional, auto-detect)'),
     ('login_btn_locator', 'Login button locator (optional, auto-detect)')],
    '''class generic_form_login:
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
            return safe_find_visible_element(self.driver, By.XPATH, "//button[1]")''' + COMMON_IMPORTS
))

# ==================== 等待操作 (op_type=11) ====================

keywords_data.append(('等待元素可见', 'wait_element_visible', 11,
    [('by_type', 'Locator type: xpath/id/css selector/name/class name/tag name/link text/partial link text'),
     ('locator', 'Element locator value'),
     ('timeout', 'Wait timeout in seconds (default 30)')],
    '''class wait_element_visible:
    """Wait for an element to become visible"""

    def __init__(self, driver):
        self.driver = driver

    def wait_element_visible(self, **kwargs):
        by_type = kwargs.get("by_type", "xpath")
        locator = kwargs.get("locator", "")
        timeout = int(kwargs.get("timeout", DEFAULT_TIMEOUT))
        if not locator:
            raise ValueError("Parameter 'locator' is required")
        by_map = {"xpath": By.XPATH, "id": By.ID, "name": By.NAME, "css selector": By.CSS_SELECTOR, "css": By.CSS_SELECTOR, "class name": By.CLASS_NAME, "tag name": By.TAG_NAME, "link text": By.LINK_TEXT, "partial link text": By.PARTIAL_LINK_TEXT}
        by = by_map.get(by_type.lower(), By.XPATH)
        safe_find_visible_element(self.driver, by, locator, timeout=timeout)
        print(f"[Wait] Element visible: {by_type}={locator}")''' + COMMON_IMPORTS
))

keywords_data.append(('等待元素消失', 'wait_element_disappear', 11,
    [('by_type', 'Locator type: xpath/id/css selector/name/class name/tag name'),
     ('locator', 'Element locator value'),
     ('timeout', 'Wait timeout in seconds (default 30)')],
    '''class wait_element_disappear:
    """Wait for an element to disappear from the page"""

    def __init__(self, driver):
        self.driver = driver

    def wait_element_disappear(self, **kwargs):
        by_type = kwargs.get("by_type", "xpath")
        locator = kwargs.get("locator", "")
        timeout = int(kwargs.get("timeout", DEFAULT_TIMEOUT))
        if not locator:
            raise ValueError("Parameter 'locator' is required")
        by_map = {"xpath": By.XPATH, "id": By.ID, "name": By.NAME, "css selector": By.CSS_SELECTOR, "css": By.CSS_SELECTOR, "class name": By.CLASS_NAME, "tag name": By.TAG_NAME}
        by = by_map.get(by_type.lower(), By.XPATH)
        try:
            WebDriverWait(self.driver, timeout, 0.5).until(EC.invisibility_of_element_located((by, locator)))
            print(f"[Wait] Element disappeared: {by_type}={locator}")
        except TimeoutException:
            print(f"[Wait] Warning: element still visible after {timeout}s: {by_type}={locator}, continuing anyway")''' + COMMON_IMPORTS
))

keywords_data.append(('等待页面加载', 'wait_page_ready_keyword', 11,
    [('timeout', 'Wait timeout in seconds (default 30)')],
    '''class wait_page_ready_keyword:
    """Wait for page to be fully loaded (document.readyState === 'complete')"""

    def __init__(self, driver):
        self.driver = driver

    def wait_page_ready_keyword(self, **kwargs):
        timeout = int(kwargs.get("timeout", 30))
        wait_page_ready(self.driver, timeout=timeout)
        print("[Wait] Page ready")''' + COMMON_IMPORTS
))

keywords_data.append(('固定等待', 'wait_fixed_seconds', 11,
    [('seconds', 'Number of seconds to wait (supports decimals, e.g. 1.5)')],
    '''class wait_fixed_seconds:
    """Fixed time wait - use only when explicit waits are not applicable"""

    def __init__(self, driver):
        self.driver = driver

    def wait_fixed_seconds(self, **kwargs):
        seconds = float(kwargs.get("seconds", 1))
        if seconds > 60:
            print(f"[Wait] Warning: long fixed wait ({seconds}s), consider using explicit waits")
        time.sleep(seconds)
        print(f"[Wait] Fixed wait {seconds}s completed")

import time'''
))

keywords_data.append(('等待文本出现', 'wait_text_present', 11,
    [('text', 'Text content to wait for'),
     ('timeout', 'Wait timeout in seconds (default 30)')],
    '''class wait_text_present:
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
            raise TimeoutException(f"Text '{text}' did not appear within {timeout}s")''' + COMMON_IMPORTS
))

keywords_data.append(('等待URL包含', 'wait_url_contains', 11,
    [('url_part', 'String that URL should contain'),
     ('timeout', 'Wait timeout in seconds (default 30)')],
    '''class wait_url_contains:
    """Wait until the URL contains a specific string (page navigation complete)"""

    def __init__(self, driver):
        self.driver = driver

    def wait_url_contains(self, **kwargs):
        url_part = kwargs.get("url_part", "")
        timeout = int(kwargs.get("timeout", DEFAULT_TIMEOUT))
        if not url_part:
            raise ValueError("Parameter 'url_part' is required")
        try:
            WebDriverWait(self.driver, timeout, 0.5).until(EC.url_contains(url_part))
            print(f"[Wait] URL contains '{url_part}': {self.driver.current_url}")
        except TimeoutException:
            raise TimeoutException(f"URL did not contain '{url_part}' within {timeout}s, current: {self.driver.current_url}")''' + COMMON_IMPORTS
))

keywords_data.append(('等待元素数量', 'wait_element_count', 11,
    [('by_type', 'Locator type: xpath/css selector/class name'),
     ('locator', 'Element locator value'),
     ('count', 'Expected minimum count (default 1)'),
     ('timeout', 'Wait timeout in seconds (default 30)')],
    '''class wait_element_count:
    """Wait until a specified number of elements appear"""

    def __init__(self, driver):
        self.driver = driver

    def wait_element_count(self, **kwargs):
        by_type = kwargs.get("by_type", "xpath")
        locator = kwargs.get("locator", "")
        count = int(kwargs.get("count", 1))
        timeout = int(kwargs.get("timeout", DEFAULT_TIMEOUT))
        if not locator:
            raise ValueError("Parameter 'locator' is required")
        by_map = {"xpath": By.XPATH, "css": By.CSS_SELECTOR, "class name": By.CLASS_NAME}
        by = by_map.get(by_type.lower(), By.XPATH)
        try:
            WebDriverWait(self.driver, timeout, 0.5).until(lambda d: len(d.find_elements(by, locator)) >= count)
            actual = len(self.driver.find_elements(by, locator))
            print(f"[Wait] Found {actual} elements (expected >= {count})")
        except TimeoutException:
            actual = len(self.driver.find_elements(by, locator))
            raise TimeoutException(f"Only {actual} elements found after {timeout}s (expected >= {count})")''' + COMMON_IMPORTS
))

# ==================== 执行 ====================
if __name__ == '__main__':
    conn = pymysql.connect(host='localhost', port=3306, user='root', password='123456', database='hcdb', charset='utf8mb4')
    cursor = conn.cursor()

    files_created = 0
    db_updated = 0

    for name, fun_name, op_type_id, params, code in keywords_data:
        # 写入文件
        write_keyword_file(fun_name, code)
        files_created += 1

        # 更新数据库
        desc_json = json.dumps([{"name": p[0], "placeholder": p[1]} for p in params], ensure_ascii=False)
        rows = update_db(fun_name, code, desc_json)
        db_updated += rows
        if rows > 0:
            print(f'  [DB] Updated {fun_name}')

    conn.commit()
    cursor.close()
    conn.close()

    print(f'\nDone: {files_created} files created, {db_updated} DB records updated')
