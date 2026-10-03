# -*- coding: UTF-8 -*-
"""
Web自动化基础工具库 - 提供健壮的Selenium操作封装
包含：智能元素查找、重试机制、等待策略、异常恢复
"""
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
    ElementNotInteractableException,
    WebDriverException,
    InvalidSelectorException
)

# 默认超时配置
DEFAULT_TIMEOUT = 30
DEFAULT_POLL = 0.5
MAX_RETRIES = 3
RETRY_DELAY = 1


def wait_page_ready(driver, timeout=30):
    """等待页面完全加载（document.readyState === 'complete'）"""
    try:
        WebDriverWait(driver, timeout, 0.5).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        print("[页面] 页面加载完成")
        return True
    except TimeoutException:
        print("[警告] 页面加载超时，但继续执行")
        return False


def safe_find_element(driver, by, value, timeout=DEFAULT_TIMEOUT, retries=MAX_RETRIES):
    """
    安全查找单个元素 - 带重试和多重容错
    支持: By.XPATH, By.CSS_SELECTOR, By.ID, By.NAME, By.TAG_NAME, By.CLASS_NAME 等
    """
    for attempt in range(retries):
        try:
            element = WebDriverWait(driver, timeout, DEFAULT_POLL).until(
                EC.presence_of_element_located((by, value))
            )
            print(f"[定位] 元素已找到: {by}={value}")
            return element
        except (TimeoutException, NoSuchElementException) as e:
            if attempt < retries - 1:
                print(f"[重试] 查找元素失败 (第{attempt+1}次): {by}={value}，{RETRY_DELAY}秒后重试...")
                time.sleep(RETRY_DELAY)
            else:
                raise NoSuchElementException(f"无法找到元素: {by}={value}，已重试{retries}次。原因: {str(e)[:200]}")
        except StaleElementReferenceException:
            if attempt < retries - 1:
                print(f"[重试] 元素已过期 (第{attempt+1}次)，重新查找...")
                time.sleep(RETRY_DELAY)
                continue
            raise


def safe_find_visible_element(driver, by, value, timeout=DEFAULT_TIMEOUT, retries=MAX_RETRIES):
    """
    安全查找可见元素 - 等待元素可见且可交互
    """
    for attempt in range(retries):
        try:
            element = WebDriverWait(driver, timeout, DEFAULT_POLL).until(
                EC.visibility_of_element_located((by, value))
            )
            return element
        except (TimeoutException, NoSuchElementException, StaleElementReferenceException) as e:
            if attempt < retries - 1:
                print(f"[重试] 等待可见元素失败 (第{attempt+1}次)，重试中...")
                time.sleep(RETRY_DELAY)
            else:
                raise NoSuchElementException(f"可见元素未找到: {by}={value}。原因: {str(e)[:200]}")


def safe_find_elements(driver, by, value, timeout=DEFAULT_TIMEOUT):
    """安全查找多个元素"""
    try:
        elements = WebDriverWait(driver, timeout, DEFAULT_POLL).until(
            EC.presence_of_all_elements_located((by, value))
        )
        return elements
    except TimeoutException:
        print(f"[警告] 未找到任何匹配元素: {by}={value}")
        return []


def scroll_to_element(driver, element, block="center"):
    """平滑滚动到元素位置"""
    try:
        driver.execute_script(
            f"arguments[0].scrollIntoView({{behavior: 'smooth', block: '{block}', inline: 'nearest'}});",
            element
        )
        time.sleep(0.3)
    except Exception as e:
        print(f"[警告] 滚动到元素失败: {e}")


def safe_click(driver, element, retries=MAX_RETRIES):
    """
    安全点击 - 处理各种点击异常
    1. 先尝试普通点击
    2. 如果被拦截，尝试移除遮挡元素
    3. 如果不可交互，尝试JS点击
    4. 处理StaleElement异常重试
    """
    for attempt in range(retries):
        try:
            scroll_to_element(driver, element)
            wait_clickable = WebDriverWait(driver, 10, 0.5).until(
                EC.element_to_be_clickable((By.XPATH, _get_element_xpath(driver, element)))
            )
            wait_clickable.click()
            print("[点击] 元素点击成功")
            return True
        except ElementClickInterceptedException:
            print(f"[警告] 点击被拦截 (第{attempt+1}次)，尝试移除遮挡...")
            try:
                driver.execute_script("""
                    var overlays = document.querySelectorAll('.el-overlay, .el-dialog__wrapper, .modal-backdrop, .el-loading-mask, .v-modal');
                    overlays.forEach(function(o) { o.style.display = 'none'; });
                """)
                time.sleep(0.3)
                element.click()
                print("[点击] 移除遮挡后点击成功")
                return True
            except Exception:
                if attempt < retries - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                raise
        except ElementNotInteractableException:
            print(f"[警告] 元素不可交互 (第{attempt+1}次)，尝试JS点击...")
            try:
                driver.execute_script("arguments[0].click();", element)
                print("[点击] JS点击成功")
                return True
            except Exception as js_e:
                if attempt < retries - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                raise RuntimeError(f"JS点击也失败: {js_e}")
        except StaleElementReferenceException:
            print(f"[重试] 元素过期 (第{attempt+1}次)，需重新获取元素")
            if attempt < retries - 1:
                time.sleep(RETRY_DELAY)
            continue
        except Exception as e:
            if attempt < retries - 1:
                print(f"[重试] 点击异常 (第{attempt+1}次): {e}")
                time.sleep(RETRY_DELAY)
            else:
                raise
    return False


def safe_input(driver, element, text, clear_first=True, retries=MAX_RETRIES):
    """
    安全输入 - 确保内容正确输入
    1. 滚动到元素
    2. 点击激活
    3. 清空（可选）
    4. 输入内容
    5. 校验输入结果
    """
    for attempt in range(retries):
        try:
            scroll_to_element(driver, element)
            element.click()
            time.sleep(0.2)

            if clear_first:
                # 多策略清空
                try:
                    element.clear()
                except Exception:
                    pass
                element.send_keys(Keys.CONTROL, "a")
                element.send_keys(Keys.BACKSPACE)
                time.sleep(0.1)

            element.send_keys(text)
            time.sleep(0.3)

            # 输入校验 (仅对input/textarea)
            if element.tag_name.lower() in ['input', 'textarea']:
                current_val = element.get_attribute("value")
                if current_val == text or text in str(current_val):
                    print(f"[输入] 输入校验成功: '{text}'")
                    # 触发事件
                    driver.execute_script(
                        "arguments[0].dispatchEvent(new Event('input', { bubbles: true }));"
                        "arguments[0].dispatchEvent(new Event('change', { bubbles: true }));",
                        element
                    )
                    return True
                else:
                    print(f"[警告] 输入校验不匹配 (第{attempt+1}次) curr='{current_val}' vs target='{text}'，JS强制写入...")
                    driver.execute_script(
                        "arguments[0].value = arguments[1];"
                        "arguments[0].dispatchEvent(new Event('input', { bubbles: true }));"
                        "arguments[0].dispatchEvent(new Event('change', { bubbles: true }));",
                        element, text
                    )
                    return True
            return True
        except StaleElementReferenceException:
            if attempt < retries - 1:
                print(f"[重试] 元素过期 (第{attempt+1}次)")
                time.sleep(RETRY_DELAY)
                continue
            raise
        except Exception as e:
            if attempt < retries - 1:
                print(f"[重试] 输入异常 (第{attempt+1}次): {e}")
                time.sleep(RETRY_DELAY)
            else:
                raise


def _get_element_xpath(driver, element):
    """从元素对象推断XPath（用于EC判断用）"""
    try:
        return driver.execute_script("""
            function getXPath(element) {
                if (element.id !== '') return '//*[@id="' + element.id + '"]';
                if (element === document.body) return '/html/body';
                var ix = 0;
                var siblings = element.parentNode.childNodes;
                for (var i = 0; i < siblings.length; i++) {
                    var sibling = siblings[i];
                    if (sibling === element)
                        return getXPath(element.parentNode) + '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
                    if (sibling.nodeType === 1 && sibling.tagName === element.tagName) ix++;
                }
            }
            return getXPath(arguments[0]);
        """, element)
    except Exception:
        return element.tag_name


def try_find_with_fallbacks(driver, strategies, timeout=DEFAULT_TIMEOUT):
    """
    多重策略查找元素 - 依次尝试直到找到
    strategies: [(by, value), (by, value), ...]
    """
    for idx, (by, value) in enumerate(strategies):
        try:
            element = safe_find_visible_element(driver, by, value, timeout=5)
            print(f"[定位] 策略{idx+1}成功: {by}={value}")
            return element
        except Exception as e:
            print(f"[定位] 策略{idx+1}失败: {by}={value} ({e})")
            continue
    raise NoSuchElementException(f"所有{len(strategies)}种定位策略均失败")


def dismiss_alerts_and_popups(driver):
    """自动处理alert/confirm弹窗"""
    try:
        alert = driver.switch_to.alert
        alert_text = alert.text
        alert.accept()
        print(f"[弹窗] 已自动关闭弹窗: {alert_text}")
        return True
    except Exception:
        return False


def ensure_element_interactable(driver, element):
    """确保元素可交互：移除可能的遮挡，滚动到视口"""
    driver.execute_script("""
        arguments[0].style.display = arguments[0].style.display || 'block';
        arguments[0].style.visibility = 'visible';
        arguments[0].style.opacity = arguments[0].style.opacity || '1';
    """, element)
    scroll_to_element(driver, element)
