import os
import requests
from bs4 import BeautifulSoup, NavigableString
from selenium.webdriver.support.wait import WebDriverWait
import time
from webtest.keyswords.ai_runtime import apply_runtime_api_key, build_headers


class ai_click:

    def __init__(self, driver):
        self.driver = driver

    # 方法入口
    def ai_click(self, **kwargs):
        # 用户传入描述
        # time.sleep(1)
        ai_step = kwargs["ai_step"]
        # 执行前刷新页面
        # self.driver.refresh()
        time.sleep(3)

        # 大模型信息
        # 配置大模型（用DeepSeek示例，兼容OpenAI接口）
        # os.environ["OPENAI_API_BASE"] = "https://api.deepseek.com/v1"
        # os.environ["OPENAI_API_KEY"] = "sk-d5c556cb0e834419a812b66782d730db"  # 替换为实际密钥
        # 公司deepseek
        ai_config = apply_runtime_api_key()
        #
        # # 初始化大模型
        """js获取html方式"""
        # js_code = "return document.body.outerHTML;"
        # # 执行JavaScript获取HTML
        # body_js = self.driver.execute_script(js_code)

        """元素获取html方式"""
        # 等待页面加载完成（包括JS执行）
        from selenium.webdriver.common.by import By
        by = By.TAG_NAME  # 正确！
        body_element = WebDriverWait(self.driver, timeout=30, poll_frequency=0.5, ignored_exceptions=None).until(
            lambda x: x.find_element(by=by, value="body"))
        body_html = body_element.get_attribute("outerHTML")
        # print("元素获取html方式html全量值:",body_html)

        """内置方法获取html方式"""
        # body_api = BeautifulSoup(self.driver.page_source, 'html.parser')

        # """可能为点击的标签<button>，<div>，<span>，<input>，<a>，<img>，<map>，<area>，<label>，<li>，<select>"""
        # 精细化-根据标签查询最有可能存在的html信息
        processed_page = self.preprocess_page(ai_step, tags_to_find=['button','span','input','a','select'], body_html=body_html)
        # 压缩过滤-传入全量-传入保留精细化签
        processed_html_all = self.process_html(str(body_html), preserve_tags=['button', 'div', 'span', 'input', 'a', 'img', 'map', 'area', 'label', 'li', 'select'])

        # print("元素获取html方式html全量值:",body_html)
        # print("元素获取html方式html全量值长度:", len(str(body_html)))

        # print("js获取html方式全量值:", body_js)
        # print("js获取html方式长度:", len(str(body_api)))

        # print("内置方法获取html全量值:", body_api)
        # print("内置方法获取html方式长度:", len(str(body_api)))

        # print("初减值:",processed_page)
        print("初减值长度:", len(str(processed_page)))
        #
        print("全量初减值:", processed_html_all)
        print("全量初减值长度:", len(str(processed_html_all)))
        #
        # """
        # 这里将processed_page细化html，与ai_step描述，与processed_page_all全量html给deepseek模型并返回给我一个xpath元素路径
        # """
        # 构造DeepSeek提示词
        if processed_page != '没有标签元素':
            prompt = f"""
            任务：分析以下网页信息，生成满足用户指令的XPath表达式

            用户指令：
            {ai_step}

            页面关键区域HTML（已筛选输入框，重点分析区域）：
            {processed_page}

            页面完整HTML（用于上下文参考，包含元素完整路径）：
            {str(processed_html_all)[:100000]}

            生成要求：
            1. 优先从【页面关键区域HTML】中定位目标元素
            2. 若关键区域HTML中存在多个候选元素，参考完整HTML中的上下文
            3. XPath确保唯一性
            4. 存在层级情况XPath生成规则：
                - parent为上一级，following-sibling为当前层级，如果label已是最后一级那么需要使用parent再使用following-sibling
                - 错误示例：//label[@title='题干']/following-sibling::div//input[@class='ant-input' and @type='text']
                - 正确示例：//label[@title='题干']/parent::div/following-sibling::div//input[@class='ant-input' and @type='text']
            5. 层级验证流程：
                - 检查label的父级div（ant-form-item-label）是否有兄弟div（ant-form-item-control）
                - 若存在，则直接使用1次parent::div+following-sibling::div
                - 若不存在，才允许向上跳转至祖父级
            6. 如果是a标签，那么优先使用id方式+层级下标方式，如果a标签没有id属性，那么查找它的父级的id属性与层级标识，最后才能谨慎使用class与name方式
                - 错误示例：//a[@class="s-top-login-btn c-btn c-btn-primary c-btn-mini lb" and @name="tj_login"]
                - 错误示例：//a[@id="s-top-loginbtn" and @name="tj_login"]
                - 正确示例：//*[@id="u"]/a[3]
                - 正确示例：//*[@id="s-top-loginbtn"]
            输出要求: 纯XPath文本，无需解释，只返回XPath表达式，不要包含任何解释或说明文字。
            """
            # 调用DeepSeek API（需替换为实际请求）
            # response = requests.post(
            #     "https://api.deepseek.com/v1/chat/completions",
            #     headers={
            #         "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
            #         "Content-Type": "application/json"
            #     },
            #     json={
            #         "model": "deepseek-chat",
            #         "messages": [{"role": "user", "content": prompt}],
            #         "temperature": 0.1,
            #         "max_tokens": 200
            #     }
            # )
            response = requests.post(
                f"{ai_config['api_base']}{ai_config['request_path']}",
                headers=build_headers(ai_config),
                json={
                    "model": ai_config["model_name"],
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "max_tokens": 200
                }
            )
            # xpath = response.json()["choices"][0]["message"]["content"].strip()
            xpath = response.json()
            xpath_value = response.json()["choices"][0]["message"]["content"]
            # print("DeepSeek返回XPath:", xpath)
            print("DeepSeekXPath:", xpath)
            print("精准DeepSeekXPath:", xpath_value)
            # 执行输入

            """模型处理-将ai_step内容传给模型，分析用户真正想输入的值"""
            # ai_step = self.input_Analysis(ai_step)
            # print("过滤后输入值:", ai_step)  # 输出: "这是一个测试示例"
            by = "xpath"
            element = WebDriverWait(self.driver, timeout=30, poll_frequency=0.5, ignored_exceptions=None).until(
                lambda x: x.find_element(by=by, value=xpath_value))
            element.click()
        else:
            print("标签不存在，不调用模型")
            assert 1 == 2

    # 初步处理
    def preprocess_page(self, ai_step, tags_to_find=None, body_html=None):
        # 初始化标签列表（默认查找input标签）
        if tags_to_find is None:
            tags_to_find = ['input']
        if body_html is None:
            print("全量html为空，不执行初步处理")
            assert 1 == 2
        # processed_page_all = BeautifulSoup(self.driver.page_source, 'html.parser')

        """逻辑执行-精细化处理-根据标签过滤后进一步匹配placeholder"""
        # soup = BeautifulSoup(body_html, 'html.parser')
        # print("ai_step:",ai_step)
        # target_html = ""
        # # 示例：针对搜索指令，重点提取搜索框和按钮区域
        # if "搜索" in ai_step or "输入" in ai_step:
        #     input_elements = soup.find_all('input') # 查找所有文本输入框
        #     # 筛选placeholder包含关键词的input元素
        #     filtered_inputs = []
        #     for input_elem in input_elements:
        #         placeholder = input_elem.get('placeholder', '')
        #         # 检查placeholder是否包含任何关键词
        #         if any(keyword in placeholder for keyword in keywords):
        #             filtered_inputs.append(input_elem)
        #         else:
        #             print("placeholder没有匹配项")
        #     if filtered_inputs:
        #         target_html = "\n".join([str(e) for e in input_elements])
        #     else:
        #         print("精细化结果为空")
        # else:
        #     # 其他指令类型，截取页面主体的前5000个字符
        #     print("当前语义缺少【搜索、输入】")
        # return f"目标区域HTML:\n{target_html}"

        """逻辑执行-精细化处理-根据传入标签匹配"""
        soup = BeautifulSoup(body_html, 'html.parser')
        print("ai_step:", ai_step)
        target_html = ""
        # 示例：针对搜索指令，重点提取搜索框和按钮区域
        # if "搜索" in ai_step or "输入" in ai_step:
        if ai_step:
            # 查找所有传入的标签元素
            all_elements = []
            # 核心修正：循环所有标签，无论是否找到元素都不提前返回
            for tag in tags_to_find:
                # 收集当前标签的所有元素
                all_elements.extend(soup.find_all(tag))
                if all_elements:
                    target_html = "\n".join([str(e) for e in all_elements])
                else:
                    pass
            # 循环结束后统一判断
            if not all_elements:
                print(f"警告：未找到任何{tags_to_find}标签元素")
                return "没有标签元素"
        else:
            # 其他指令类型，截取页面主体的前5000个字符
            target_html = str(soup.body)[:5000]
            print("当前描述为空，已截取页面主体")
        return f"目标区域HTML:\n{target_html}"

    # 压缩过滤处理
    def process_html(self, full_html, preserve_tags):
        soup = BeautifulSoup(full_html, 'html.parser')
        for tag in soup.find_all(True):  # 只处理标签节点
            if tag.name not in preserve_tags:
                tag.attrs = {}  # 移除所有属性
                # 保留子标签结构，但清空文本内容
                for child in list(tag.children):
                    if isinstance(child, NavigableString):
                        child.extract()  # 移除文本节点，但保留标签节点
        # 转换为字符串并清理多余空白
        result = str(soup).replace('\n', '').replace('\r', '').replace('  ', '')
        return result

    # 实际值提取
    def input_Analysis(self, ai_step):
        prompt = f"""
        任务：从用户指令中提取需要输入的具体内容

        用户指令：
        {ai_step}

        提取要求：
        1. 忽略操作词（如"输入"、"搜索"、"查询"等）
        2. 提取核心输入内容（如ID、关键词、文本等）
        3. 保留完整语义（如"今天天气"而非"今天"）
        4. 若指令中无明确输入内容，返回空字符串

        输出要求：纯文本，无需解释
        """
        # 调用大模型API
        # response = requests.post(
        #     "https://api.deepseek.com/v1/chat/completions",
        #     headers={
        #         "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
        #         "Content-Type": "application/json"
        #     },
        #     json={
        #         "model": "deepseek-chat",
        #         "messages": [{"role": "user", "content": prompt}],
        #         "temperature": 0.1,
        #         "max_tokens": 100
        #     }
        # )
        response = requests.post(
            f"{ai_config['api_base']}{ai_config['request_path']}",
            headers=build_headers(ai_config),
            json={
                "model": ai_config["model_name"],
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "max_tokens": 200
            }
        )
        try:
            print("用户指令中提取需要输入的具体内容为:", response.json())
            return response.json()["choices"][0]["message"]["content"].strip()
        except:
            # 失败时使用启发式提取
            print("模型未能获取成功")
            return "模型未能获取成功"
