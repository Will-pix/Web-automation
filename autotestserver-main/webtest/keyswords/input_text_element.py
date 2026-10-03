class input_text_element:
    """
    智能“万能输入”关键字库 V4 (下拉框/伪输入框适配版)
    修复问题：解决 'Select' 组件或 '伪输入框' 无法通过 placeholder 定位 input 的问题。
    """
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)
        print("自定义输入关键字库(input_text_element V4)已加载")
    def input_text_element(self, text, xpath=" ", placeholder=" ", label_text=" ", index=0, **kwargs):
        """
        万能输入主方法
        """
        # --- 1. 参数清洗 ---
        target_text = str(text) if text else ""
        p_xpath = str(xpath).strip() if xpath else ""
        p_placeholder = str(placeholder).strip() if placeholder else ""
        p_label = str(label_text).strip() if label_text else ""
        try:
            idx = int(index)
        except:
            idx = 0
        if not target_text:
            raise ValueError("调用失败：参数 'text' 不能为空")
        print(f"\n--- 开始执行[万能输入 V4] ---")
        print(f"输入内容: '{target_text}'")
        target_element = None
        strategy_log = ""
        # --- 2. 智能定位策略 (多阶段查找) ---
        try:
            # === 策略 A: XPath (最高优先级) ===
            if p_xpath:
                strategy_log = f"XPath: {p_xpath}"
                final_xpath = p_xpath
                # 自动修正: 如果定位的不是 input/textarea，尝试找内部 input
                if not p_xpath.endswith("input") and not p_xpath.endswith("textarea"):
                    final_xpath = f"({p_xpath})//input | ({p_xpath})//textarea | {p_xpath}"
                target_element = self._find_element(final_xpath, idx)
            # === 策略 B: Placeholder (最强容错逻辑) ===
            elif p_placeholder:
                strategy_log = f"提示词: {p_placeholder}"
                # 1. 尝试找标准的 input/textarea
                xpath_std = f"//input[contains(@placeholder, '{p_placeholder}')] | //textarea[contains(@placeholder, '{p_placeholder}')]"
                try:
                    target_element = self._find_element(xpath_std, idx)
                except TimeoutException:
                    print(" ⚠️ 标准Input未找到，尝试查找“伪输入框”(div/span)...")
                    # 2. [关键改进] 尝试找包含该文字的 div/span/label (针对下拉框/伪输入框)
                    # 排除 script 标签，且该元素可见
                    xpath_text = f"//*[contains(text(), '{p_placeholder}') and not(self::script)]"
                    target_element = self._find_element(xpath_text, idx)
                    print(f" ✅ 成功定位到伪输入框: <{target_element.tag_name}>")
            # === 策略 C: Label ===
            elif p_label:
                strategy_log = f"标签名: {p_label}"
                xpath_label = f"//*[contains(text(), '{p_label}')]/following::input[1] | //*[contains(text(), '{p_label}')]/following::textarea[1]"
                target_element = self._find_element(xpath_label, idx)
            else:
                raise ValueError("参数全空，无法定位")
        except Exception as e:
            raise RuntimeError(f"定位失败。策略: {strategy_log}。原因: {str(e).splitlines()[0]}")
        # --- 3. 智能交互 (点击 & 输入) ---
        print(f" 📍 操作元素: <{target_element.tag_name}> (策略: {strategy_log})")
        try:
            # 滚动至可见
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", target_element)
            time.sleep(0.5)
            # 判断是否是伪输入框 (非 input/textarea)
            is_fake_input = target_element.tag_name.lower() not in ['input', 'textarea']
            if is_fake_input:
                print(" 🖱️ 检测到非标准输入框，尝试先点击激活...")
                target_element.click()
                time.sleep(0.5)
                # 点击后，焦点通常会转移到生成的真实 input 或自身
                # 尝试向“当前焦点元素”输入，或者继续操作原元素
                try:
                    active_ele = self.driver.switch_to.active_element
                    if active_ele and active_ele.tag_name == 'input':
                        print(" 🔀 焦点已切换至内部 Input，转向操作焦点元素")
                        target_element = active_ele
                except:
                    pass
            # --- 4. 执行清空与输入 ---
            # 4.1 模拟键盘清空
            try:
                target_element.click()
            except:
                pass
            target_element.send_keys(Keys.CONTROL, "a")
            target_element.send_keys(Keys.BACKSPACE)
            time.sleep(0.2)
            # 4.2 输入
            target_element.send_keys(target_text)
            # 4.3 如果是下拉选择框，输入后通常需要回车选中
            if is_fake_input:
                time.sleep(0.5)
                target_element.send_keys(Keys.ENTER)
                print(" ↵ 已发送回车键 (针对下拉搜索框)")
            time.sleep(0.5)
            # --- 5. 兜底校验 ---
            # 注意：对于 div 类型的伪输入框，getValue 可能无效，这里仅对 input 做强校验
            if target_element.tag_name in ['input', 'textarea']:
                current_val = target_element.get_attribute("value")
                if current_val != target_text and target_text not in str(current_val):
                    print(f" ⚠️ 常规输入未生效 (Curr: {current_val})，执行JS强制写入...")
                    self._js_force_input(target_element, target_text)
                else:
                    # 触发事件以防万一
                    self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", target_element)
            print(f" ✅ 输入流程结束")
        except Exception as e:
            raise RuntimeError(f"交互失败。详情: {str(e)}")
    def _find_element(self, xpath, idx):
        """辅助查找方法"""
        elements = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, xpath)))
        # 优先找可见的
        visible_elements = [e for e in elements if e.is_displayed()]
        if visible_elements:
            return visible_elements[idx] if len(visible_elements) > idx else visible_elements[0]
        return elements[idx] if len(elements) > idx else elements[0]
    def _js_force_input(self, element, text):
        """JS 强制设值"""
        js = """
            arguments[0].value = arguments[1];
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
        """
        self.driver.execute_script(js, element, text)
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
# 假设这是你的全局上下文，保持原样
from webtest.tool.webrun.core.globalContext import g_context
