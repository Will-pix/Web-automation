class click_text_element:
    """
    智能“万能点击”关键字库 V3 (增强版)：
    1. 解决侧边栏/嵌套菜单点击难问题（自动向上查找可点击父级）。
    2. 解决文本含空格/换行问题（使用 normalize-space）。
    3. 强化 JS 强制点击，应对被遮挡或隐藏元素。
    """
    def __init__(self, driver):
        self.driver = driver
        self.default_wait_time = 10
        self.wait = WebDriverWait(self.driver, self.default_wait_time)
        print("自定义点击关键字库(click_text_element V3 - 深度穿透版)已加载")
    @staticmethod
    def _escape_xpath_text(text):
        """
        处理XPath文本：
        1. 处理单引号。
        2. 返回用于 normalize-space 的比较字符串。
        """
        if "'" in text:
            # 如果包含单引号，使用 concat 处理（略复杂但稳健），或者简单用双引号
            return f'"{text}"'
        return f"'{text}'"
    def _highlight_element(self, element):
        """(可选) 高亮显示将要点击的元素，便于调试"""
        try:
            self.driver.execute_script("arguments[0].style.border='3px solid red'", element)
        except:
            pass
    def click_text_element(self, **kwargs):
        """
        万能点击方法 V3
        :param kwargs:
            - text_to_click (str): 目标文本
            - container_xpath (str): 限定容器
            - exact_match (bool): 是否精确匹配文本（默认 False，使用包含匹配）
            - force_js (bool): 是否直接使用JS点击（默认 False，失败后自动尝试）
        """
        text_to_click = kwargs.get("text_to_click")
        container_xpath = kwargs.get("container_xpath", "").strip()
        exact_match = kwargs.get("exact_match", False)

        if not text_to_click:
            raise ValueError("必须提供 text_to_click 参数")
        print(f"\n--- 开始执行[万能点击 V3] ---")
        print(f"目标: [{text_to_click}] | 容器: {container_xpath if container_xpath else '全页面'}")
        search_root = container_xpath if container_xpath else ""
        escaped_text = self._escape_xpath_text(text_to_click)
        # --- 核心改进 1: 构建更智能的 XPath ---
        # 使用 normalize-space() 忽略 HTML 源码中的前后空格和换行
        if exact_match:
            # 精确匹配：HTML显示的文字必须完全等于目标
            text_condition = f"normalize-space(text())={escaped_text}"
        else:
            # 包含匹配：HTML显示的文字包含目标
            text_condition = f"contains(normalize-space(text()), {escaped_text})"
        # 策略列表
        # 1. 查找包含文字的最底层元素 (text node 的父级)
        # 2. 查找 value 属性包含文字的元素 (针对 input 按钮)
        # 3. 查找 title 或 aria-label 包含文字的元素 (针对图标按钮)
        strategies = [
            (f"{search_root}//*[not(self::script) and {text_condition}]", "最深层文本节点"),
            (f"{search_root}//input[contains(@value, {escaped_text})]", "Input按钮值"),
            (f"{search_root}//*[@title={escaped_text} or contains(@aria-label, {escaped_text})]", "Title/Label属性")
        ]
        target_element = None
        found_by = ""
        # --- 阶段一：定位元素 ---
        for xpath, strategy_name in strategies:
            try:
                # 这里使用 presence 而不是 clickable，因为侧边栏元素可能是不可见的或被折叠的
                # 我们先找到它，再想办法点它
                elements = self.driver.find_elements(By.XPATH, xpath)

                # 过滤逻辑：优先找可见的；如果都不可见，取第一个存在的
                visible_elements = [e for e in elements if e.is_displayed()]

                if visible_elements:
                    target_element = visible_elements[-1] # 通常取最后一个匹配项更精确（或者是层级最深的）
                    found_by = f"{strategy_name} (可见)"
                    break
                elif elements:
                    # 找到了但不可见（可能是折叠菜单），先存着做备选
                    target_element = elements[0]
                    found_by = f"{strategy_name} (隐藏)"
                    # 不 break，继续找有没有可见的
            except Exception:
                continue
        if not target_element:
            raise NoSuchElementException(f"未在页面找到包含文本 '{text_to_click}' 的任何元素。")
        print(f" 📍 已定位元素 [{found_by}] -> 标签: <{target_element.tag_name}>")
        # --- 阶段二：智能向上查找可点击父级 ---
        # 很多时候文字在 span 里，但 click 事件在 div/a/li 上
        final_element = target_element
        # 如果当前元素显然不是交互元素（如 span, b, i, strong），尝试向上找几层
        non_interactive_tags = ['span', 'b', 'i', 'strong', 'em', 'div', 'p', 'label']

        # 尝试向上冒泡找 clickable 的祖先 (最多找 3 层)
        if final_element.tag_name.lower() in non_interactive_tags:
            try:
                # 检查父级是否是 a, button 或有 cursor:pointer 样式
                for _ in range(3):
                    parent = final_element.find_element(By.XPATH, "./..")
                    tag = parent.tag_name.lower()
                    # 获取 cursor 样式来判断是否可点击
                    cursor = parent.value_of_css_property("cursor")

                    if tag in ['a', 'button'] or cursor == 'pointer' or 'btn' in parent.get_attribute("class") or 'menu' in parent.get_attribute("class"):
                        final_element = parent
                        print(f" 🔼 自动定位到父级可点击元素: <{tag}> (样式: {cursor})")
                        break
                    # 继续向上
                    final_element = parent
            except:
                # 如果报错（比如到了 root），就回退到原始元素
                final_element = target_element
        self._highlight_element(final_element)
        # --- 阶段三：执行点击 (三层保障) ---
        try:
            # 1. 尝试滚动到可见区域
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", final_element)
            time.sleep(0.5) # 等待滚动动画
            # 2. 尝试常规点击
            print(" 🖱️ 尝试常规点击...")
            final_element.click()
            print(f" ✅ 成功点击: '{text_to_click}'")
            return
        except Exception as e:
            print(f" ⚠️ 常规点击失败 ({str(e).splitlines()[0]})...")
        try:
            # 3. 尝试 ActionChains 点击 (模拟鼠标移动过去点，对 hover 菜单有效)
            print(" 🖱️ 尝试 ActionChains 点击...")
            from selenium.webdriver.common.action_chains import ActionChains
            actions = ActionChains(self.driver)
            actions.move_to_element(final_element).click().perform()
            print(f" ✅ ActionChains 点击成功")
            return
        except Exception as e:
             print(f" ⚠️ ActionChains 点击失败...")
        try:
            # 4. 终极方案：JS 强制点击
            # 即使元素被遮挡、隐藏或 height=0，这通常也能触发
            print(" 🚀 启动终极方案: JS 强制点击...")
            self.driver.execute_script("arguments[0].click();", final_element)
            print(f" ✅ JS 强制点击成功")
        except Exception as e:
            raise RuntimeError(f" ❌ 所有点击策略均失败，无法点击文本 '{text_to_click}'。错误: {e}")
import difflib
import json
import os
import re
import time
from selenium.webdriver.support.wait import WebDriverWait
from app import application
from webtest.tool.webrun.core.globalContext import g_context
import requests
