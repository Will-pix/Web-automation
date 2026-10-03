class ai_action_merge:
    def __init__(self, driver):
        self.driver = driver
    # 总方法入口
    def ai_action_merge(self, **kwargs):
        ai_step = kwargs["ai_step"]
        action_step = self.Analysis_aciton(ai_step)
        print("分解的步骤为:",action_step)
        # 转为字典
        action_step = json.loads(action_step)
        # 遍历步骤
        for i in action_step:
            time.sleep(2)
            os.environ["OPENAI_API_KEY"] = "8ceb8471-e3bf-4fe5-9fff-eaa9b37ec08d"
            print("每次的步骤是",i)
            if i["type"] == "点击":
                self.click_aciton(i["step"])
            elif i["type"] == "输入":
                self.input_action(i["step"])
            elif i["type"] == "悬停":
                self.hover_aciton(i["step"])
            elif i["type"] == "拖拽":
                self.drag_action(i["step"])
            elif i["type"] == "滑动":
                self.slide_action(i["step"])
            elif i["type"] == "等待":
                self.sleeptime_action(i["step"])
            elif i["type"] == "断言":
                self.ai_assert(i["step"])
            elif i["type"] == "判断":
                self.ai_choice_image(i["step"])
    # 分析-这是方法-分析语义，并且返回标识key-点击/输入/悬浮
    def Analysis_aciton(self,ai_step):
        os.environ["OPENAI_API_KEY"] = "8ceb8471-e3bf-4fe5-9fff-eaa9b37ec08d"
        prompt = f"""
任务目标
对用户指令的执行步骤文本进行精准语义切割，按规则完成点击、输入、悬浮、拖拽、滑动、等待、断言、判断 8 类操作类型的无歧义归类，输出标准格式结果，用于APP自动化测试流程解析。
用户指令：{ai_step}
【核心执行逻辑】
1. 先执行语义分割：严格按文本切割标准拆分独立步骤，确保步骤语义完整；
2. 再执行类型判定：对拆分后的单个步骤，按优先级规则顺序匹配，避免多规则冲突导致的误判。
【核心优先级规则（类型判定阶段强制遵循，从高到低）】
1. 判断类型专项规则优先级最高：只要步骤满足 “条件逻辑 + 执行逻辑” 结构，无论是否符合其他规则，均优先判定为判断类型；
2. 滑动 / 拖拽区分规则次之：明确动作属性，避免两类位移操作混淆；
3. 多执行动作分割规则再次之：仅处理判断步骤中多余的执行动作；
4. 类型归类规则为兜底规则：仅适用于不满足前 3 条规则的步骤。
【1. 文本切割强制标准】
1. 一个独立动作对应一个步骤，除判断有逻辑关联的动作其它所有操作均必须拆分；
2. 属于同一逻辑单元的动作（如判断步骤内的条件 + 执行动作），不拆分内部结构；
3. 步骤语义必须完整保留，不得删减、缩写任何要素（如保留 “今天天气” 而非 “今天”）。
【2. 操作类型精准判定标准（仅可选择以下 8 类，无例外）】
1. 点击：主动触发元素的单次按压操作，无法归类的动作均归为此类，典型场景为点击返回按钮、点击搜索图标、点击发送验证码、点击弹窗确认
2. 输入：向可输入元素填充文本内容的操作，典型场景为输入用户名 admin、输入收货地址、输入支付密码 123456
3. 悬停：鼠标悬浮/悬停展开选项或二级菜单的动作，典型场景为悬浮/悬停在哪个菜单上，悬浮/悬停在习题管理功能上，悬浮/悬停在小狗的头上
4. 拖拽：语义含 “拖拽” 必须归为此类；将元素从原位置移动到目标位置的主动位移操作，典型场景为拖拽小狗到 dog 区域上、将浮动的黑色帽子拖拽到小孩的头上
5. 滑动：页面 / 控件内的被动位移操作（无目标元素拖拽），典型场景为向上滑动商品列表、左右滑动切换 TAB 栏、下滑至底部
6. 等待：等待页面加载 / 元素出现 / 状态变更的操作，典型场景为等待一会，等待几秒
7. 断言：验证元素状态 / 数据是否符合预期的验证操作，典型场景为断言页面标题为我的订单、断言订单金额为 100 元、断言按钮状态为禁用
8. 判断：满足 “条件逻辑 + 执行逻辑” 结构的操作，按专项规则判定，典型场景为若登录成功则进入首页、检查元素存在就点击确认
【3. 判断类型识别专项规则】
1. 若某段内容同时包含条件逻辑和执行逻辑（即 “满足 XX 条件，就执行 XX 操作” 的结构），无论是否包含 “是否 / 有没有 / 检查 / 判断 / 如果” 等关键词，该内容均为判断步骤的完整语义，必须作为一个独立步骤，不拆分内部逻辑；
2. 常见条件逻辑标识：如果、若、要是、假如、是否、有没有、检查、判断；
3. 常见执行逻辑标识：就、则、便、才、有就、没有就；
4. 满足上述结构的步骤，类型强制归为判断。
【4. 多执行动作分割规则】
1. 判断步骤仅能带一个紧跟的执行动作；
2. 多余执行动作（用 “并 / 且 / 同时” 连接）需分割为独立普通步骤，类型匹配动作本身。
【5. 滑动与拖拽区分规则】
1. 语义中明确包含 “拖拽” 词汇 → 类型强制为拖拽；
2. 无明确拖拽对象，仅页面 / 控件内位移 → 类型为滑动。
【输出格式强制约束】
1. 最终输出为标准 JSON 格式，无多余标点、换行或注释；
2. 字段要求：
   - order：连续正整数（1,2,3...），按步骤执行顺序排列；
   - type：仅允许填入 8 种类型（点击 / 输入 / 长按 / 拖拽 / 滑动 / 等待 / 断言 / 判断），不得出现其他值；
   - step：保留原句完整语义，不修改任何文字；
3. 格式示例：
[
    {{"order":1,"type":"判断","step":"如果登录成功，则点击首页按钮"}},
    {{"order":2,"type":"点击","step":"查看用户信息"}}
]
【典型场景示例（强制参照执行）】
示例 1：判断步骤 + 多动作分割
原句：如果登录成功，则点击首页按钮并查看用户信息
输出结果：
[
    {{"order":1,"type":"判断","step":"如果登录成功，则点击首页按钮"}},
    {{"order":2,"type":"点击","step":"查看用户信息"}}
]
示例 2：滑动 vs 拖拽区分
原句：向上滑动商品列表查看更多；拖拽商品到收藏夹
输出结果：
[
    {{"order":1,"type":"滑动","step":"向上滑动商品列表查看更多"}},
    {{"order":2,"type":"拖拽","step":"拖拽商品到收藏夹"}}
]
示例 3：多连续动作拆分
原句：点击搜索框输入今天天气
输出结果：
[
    {{"order":1,"type":"点击","step":"点击搜索框"}},
    {{"order":2,"type":"输入","step":"输入今天天气"}}
]
示例 4：兜底规则应用（无法分类归为点击）
原句：刷新当前页面
输出结果：
[
    {{"order":1,"type":"点击","step":"刷新当前页面"}}
]
示例 5：APP专属长按类型识别
原句：长按聊天消息弹出删除选项
输出结果：
[
    {{"order":1,"type":"长按","step":"长按聊天消息弹出删除选项"}}
]
"""
        pass
        # 调用大模型API-公司豆包1.6
        response = requests.post(
            "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
            headers={
                "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
                "Content-Type": "application/json"
            },
            json={
                "model": "doubao-seed-1-6-250615",
                "temperature" : 0.2,
                "reasoning_effort": "medium",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "text": prompt,
                                "type": "text"
                            }
                        ]
                    }
                ],
                "thinking": {
                    "type": "auto"
                }
            }
        )
        try:
            # print("用户指令中提取需要输入的具体内容为:", response.json()["choices"][0]["message"]["content"].strip())
            return response.json()["choices"][0]["message"]["content"].strip()
        except:
            # 失败时使用启发式提取
            print("模型未能获取成功")
            return "模型未能获取成功"
    # 点击-这是点击调用方法入口
    def click_aciton(self,step):
        # 调用上传并获取坐标
        coordinate = self.screenshot_up(step)
        abs_x = coordinate["abs_x"]
        abs_y = coordinate["abs_y"]
        """这是相对与一个元素的坐标点击"""
        # 创建一个固定在视口左上角的临时元素
        self.driver.execute_script("""
                  const origin = document.createElement('div');
                  origin.id = 'viewport-origin';
                  origin.style = 'position:fixed;left:0;top:0;width:1px;height:1px;z-index:9999';
                  document.body.appendChild(origin);
              """)
        # 定位这个元素并基于它点击
        origin = self.driver.find_element(By.ID, 'viewport-origin')
        ActionChains(self.driver).move_to_element_with_offset(origin, abs_x, abs_y).click().perform()
        # 移除临时元素
        # self.driver.execute_script("document.getElementById('viewport-origin').remove();")
        self.driver.execute_script("""
                const element = document.getElementById('viewport-origin');
                if (element) {  // 仅当元素存在时才执行删除
                    element.remove();
                }
            """)
    # 输入-这是输入调用方法入口
    def input_action(self, step):
        # 先调用语义过滤
        input_value = self.input_Analysis(step)
        # 调用上传并获取坐标
        coordinate = self.screenshot_up(step)
        abs_x = coordinate["abs_x"]
        abs_y = coordinate["abs_y"]
        """这是相对与一个元素的坐标点击"""
        # 创建一个固定在视口左上角的临时元素
        self.driver.execute_script("""
                  const origin = document.createElement('div');
                  origin.id = 'viewport-origin';
                  origin.style = 'position:fixed;left:0;top:0;width:1px;height:1px;z-index:9999';
                  document.body.appendChild(origin);
              """)
        # 定位这个元素并基于它点击
        origin = self.driver.find_element(By.ID, 'viewport-origin')
        ActionChains(self.driver).move_to_element_with_offset(origin, abs_x, abs_y).click().perform()
        time.sleep(0.5)  # 等待输入框激活
        flask_env = os.getenv('FLASK_ENV', 'development')
        if flask_env == 'production':
            print("执行了CONTROL")
            ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
        else:
            print("执行了COMMAND")
            ActionChains(self.driver).key_down(Keys.COMMAND).send_keys('a').key_up(Keys.COMMAND).perform()
        ActionChains(self.driver).send_keys(Keys.DELETE).perform()
        # 输入新内容
        # 调用模型拆解内容
        ActionChains(self.driver).send_keys(input_value).perform()
        # 移除临时元素
        # self.driver.execute_script("document.getElementById('viewport-origin').remove();")
        # 将原来的直接删除改为带判断的删除
        self.driver.execute_script("""
                const element = document.getElementById('viewport-origin');
                if (element) {  // 仅当元素存在时才执行删除
                    element.remove();
                }
            """)
    # 悬浮-这是悬浮调用方法入口
    def hover_aciton(self,step):
        # 调用上传并获取坐标
        coordinate = self.screenshot_up(step)
        abs_x = coordinate["abs_x"]
        abs_y = coordinate["abs_y"]
        """这是相对与一个元素的坐标点击"""
        # 创建一个固定在视口左上角的临时元素
        self.driver.execute_script("""
                  const origin = document.createElement('div');
                  origin.id = 'viewport-origin';
                  origin.style = 'position:fixed;left:0;top:0;width:1px;height:1px;z-index:9999';
                  document.body.appendChild(origin);
              """)
        # 定位这个元素并基于它点击
        origin = self.driver.find_element(By.ID, 'viewport-origin')
        ActionChains(self.driver).move_to_element_with_offset(origin, abs_x, abs_y).perform()
        time.sleep(0.5)
        # 移除临时元素
        # self.driver.execute_script("document.getElementById('viewport-origin').remove();")
        self.driver.execute_script("""
                const element = document.getElementById('viewport-origin');
                if (element) {  // 仅当元素存在时才执行删除
                    element.remove();
                }
            """)
    # 这是输入的语义分析调用的方法
    def input_Analysis(self, ai_step):
        prompt = f"""
        任务：从输入类型的步骤中提取核心输入内容
        用户指令步骤：{ai_step}
提取要求：
1.  定位独立动词类操作词：输入、填写、录入、搜索、查询、查找等
    - 仅识别作为独立动作的操作词，排除作为名词/定语的情况（如"查询表"中的"查询"不视为操作词）
2.  忽略内容范围：
    - 操作词本身
    - 操作词前后的修饰性文本：[任意字符]为、的[任意字符]、[任意字符]处、[任意字符]里、[任意字符]中
    - 所有非成对标注的无关标点：冒号、顿号、逗号等
3.  提取规则（优先级从高到低）：
    3.1  优先识别**成对标注符号**包裹的内容：
         - 成对标注符号定义：左右对称、用于凸显内容的符号（如【】、[]、""、''、<>、《》、()等）
         - 提取逻辑：识别步骤中所有成对闭合的标注符号，提取其包裹的核心文本；多个成对符号时取最后一个符号内的内容
         - 异常降级：符号不闭合/不成对时，跳过此规则，执行后续提取逻辑
    3.2  仅保留操作词直接指向的核心文本内容，删除前后多余空格
    3.3  单句仅提取1个核心输入内容，若存在多个操作词取最后一个操作词对应的内容
4.  异常处理：
    - 若步骤无明确输入内容（如仅"输入""搜索"），返回空字符串
    - 若操作词后无有效文本，返回空字符串
    - 若成对符号包裹内容为空（如""），按原规则提取或返回空
5.  输出要求：纯文本，无解释、无标点、无冗余空格、无额外字符
        """
        # 调用大模型API-公司豆包1.6
        response = requests.post(
            "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
            headers={
                "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
                "Content-Type": "application/json"
            },
            json={
                "model": "doubao-seed-1-6-250615",
                "temperature": 0.2,
                "reasoning_effort": "medium",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "text": prompt,
                                "type": "text"
                            }
                        ]
                    }
                ],
                "thinking": {
                    "type": "disabled"
                }
            }
        )
        try:
            print("用户指令中提取需要输入的具体内容为:", response.json())
            return response.json()["choices"][0]["message"]["content"].strip()
        except:
            # 失败时使用启发式提取
            print("模型未能获取成功")
            return "模型未能获取成功"
    # 这是截图上传调用的方法并返回坐标
    def screenshot_up(self,step):
        screenshot = self.driver.get_screenshot_as_png()
        screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')
        os.environ["OPENAI_API_KEY"] = "8ceb8471-e3bf-4fe5-9fff-eaa9b37ec08d"
        prompt = f"""
                需求：按照指令描述查找交互元素的坐标位置方便后续操作，
                指令：{step}
                返回bbox格式为严格字典：{{"x1": 数字, "y1": 数字，"x2": 数字, "y2": 数字}}
                返回格式不能存在尾部有多余的符号如逗号等，影响整体数据结构
                【查找规则】：如果在截图中找不到指令描述的元素，直接返回纯文本“无”，不返回任何其他内容
                """
        response = requests.post(
            "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
            headers={
                "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
                "Content-Type": "application/json"
            },
            json={
                "model": "doubao-1-5-ui-tars-250428",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{screenshot_b64}"},
                                "detail": "high"
                            }, {
                                "type": "text",
                                "text": prompt,
                            }
                        ]
                    }
                ]
                ,
                "thinking": {
                    "type": "disabled"
                }
                ,
                "image_pixel_limit": {
                    "max_pixels": 4014080,
                    "min_pixels": 3136
                }
            }
        )
        # print(response.request.body)
        xpath = response.json()
        xpath_value = response.json()["choices"][0]["message"]["content"]
        print("豆包返回值:", xpath)
        print("豆包精准值:", xpath_value)
        # 2. 模型返回“无”：找不到元素，中断执行并说明原因
        if xpath_value == "无":
            error_msg = f"ui-tars模型未找到指定元素，请检查上传截图是否正确，指令：{step}"
            print(error_msg)
            raise ValueError(error_msg)  # 抛异常，明确是“找不到元素”
        # 模型调用失败直接抛异常
        if response.status_code != 200:
            print("模型调用失败")
            assert 1 == 2
        content = response.json()["choices"][0]["message"]["content"].strip()
        if not (content.startswith('{') and content.endswith('}')):
            print("模型返回非JSON格式")
            assert 1 == 2
        # 坐标换算
        coords_dict = json.loads(content)
        # 获取浏览器窗口总高度（含导航栏）
        window_height = self.driver.get_window_size()["height"]  # 比如 1080px
        print("浏览器窗口总高度",window_height)
        #
        # 获取网页内容区域高度（不含导航栏）
        content_height = self.driver.execute_script("return window.innerHeight")
        print("网页内容区域高度",content_height)
        # 获取浏览器窗口总宽度
        window_size = self.driver.get_window_size()
        window_width = window_size["width"]  # 动态获取窗口宽度
        print("浏览器窗口总宽度", window_width)
        screen_width = self.driver.execute_script("return window.screen.width")
        print("屏幕总宽度", screen_width)
        # 计算导航栏高度
        nav_height = window_height - content_height  # 通常在 60-100px 左右（因浏览器版本/系统而异）
        print("导航栏高度",nav_height)
        # # 解析坐标（失败直接报错）
        print("返回坐标",coords_dict)
        x1 = coords_dict["x1"]
        x2 = coords_dict["x2"]
        y1 = coords_dict["y1"]
        y2 = coords_dict["y2"]
        # 假设模型返回的坐标是 (x1, y1, x2, y2)
        x_center = (x1 + x2) / 2  # 计算中心点 x 坐标
        y_center = (y1 + y2) / 2  # 计算中心点 y 坐标
        # 屏幕分辨率
        screen_width = int(window_width)
        screen_height = int(content_height)
        # 计算实际屏幕坐标
        abs_x = (x_center / 1000) * screen_width
        abs_y = (y_center / 1000) * screen_height
        print("abs_x", abs_x)
        print("abs_y", abs_y)
        return {"abs_x":abs_x,"abs_y":abs_y}
    # 拖拽-这是拖拽的调用方法入口
    def drag_action(self, step):
        # 调用上传并获取坐标
        coordinate = self.drag_screenshot_up(step)
        start_abs_x = coordinate["start_abs_x"]
        start_abs_y = coordinate["start_abs_y"]
        end_abs_x = coordinate["end_abs_x"]
        end_abs_y = coordinate["end_abs_y"]
        # 创建临时元素作为拖拽参考点
        self.driver.execute_script("""
            const origin = document.createElement('div');
            origin.id = 'viewport-origin';
            origin.style = 'position:fixed;left:0;top:0;width:1px;height:1px;z-index:9999';
            document.body.appendChild(origin);
        """)
        origin = self.driver.find_element(By.ID, 'viewport-origin')
        # 执行拖拽操作
        actions = ActionChains(self.driver)
        actions.move_to_element_with_offset(origin, start_abs_x, start_abs_y)
        actions.click_and_hold()
        actions.move_to_element_with_offset(origin, end_abs_x, end_abs_y)
        actions.release()
        actions.perform()
        # 移除临时元素
        # self.driver.execute_script("document.getElementById('viewport-origin').remove();")
        self.driver.execute_script("""
                const element = document.getElementById('viewport-origin');
                if (element) {  // 仅当元素存在时才执行删除
                    element.remove();
                }
            """)
    # 拖拽-这是拖拽的截图上传调用方法并返回多个坐标
    def drag_screenshot_up(self,step):
        screenshot = self.driver.get_screenshot_as_png()
        screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')
        os.environ["OPENAI_API_KEY"] = "8ceb8471-e3bf-4fe5-9fff-eaa9b37ec08d"
        prompt = f"""
               需求：按照指令描述查找起始元素和目标位置的坐标，用于拖拽操作
               指令：{step}
               返回格式为包含起始和终点坐标的严格字典：
               {{"start_x1": 数字, "start_y1": 数字, "start_x2": 数字, "start_y2": 数字,
               "end_x1": 数字, "end_y1": 数字, "end_x2": 数字, "end_y2": 数字}}
                返回格式不能存在尾部有多余的符号如逗号等，影响整体数据结构
                【查找规则】：如果在截图中找不到指令描述的元素，直接返回纯文本“无”，不返回任何其他内容
               """
        response = requests.post(
            "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
            headers={
                "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
                "Content-Type": "application/json"
            },
            json={
                "model": "doubao-1-5-ui-tars-250428",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{screenshot_b64}"
                                },
                                "detail": "high"
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ],
                "thinking": {
                    "type": "disabled"
                },
                "image_pixel_limit": {
                    "max_pixels": 4014080,
                    "min_pixels": 3136
                }
            }
        )
        xpath_value = response.json()["choices"][0]["message"]["content"]
        # 2. 模型返回“无”：找不到元素，中断执行并说明原因
        if xpath_value == "无":
            error_msg = f"ui-tars模型未找到指定元素，请检查上传截图是否正确，指令：{step}"
            print(error_msg)
            raise ValueError(error_msg)  # 抛异常，明确是“找不到元素”
        # 模型调用失败直接抛异常
        if response.status_code != 200:
            print("模型调用失败")
            assert 1 == 2
        content = response.json()["choices"][0]["message"]["content"].strip()
        xpath = response.json()
        print("拖拽操作返回具体内容为",xpath)
        if not (content.startswith('{') and content.endswith('}')):
            print("模型返回非JSON格式")
            assert 1 == 2
        print("拖拽坐标返回值:", content)
        # 获取浏览器窗口高度信息
        window_height = self.driver.get_window_size()["height"]
        content_height = self.driver.execute_script("return window.innerHeight")
        nav_height = window_height - content_height
        # 获取浏览器窗口总宽度
        window_size = self.driver.get_window_size()
        window_width = window_size["width"]  # 动态获取窗口宽度
        print("浏览器窗口总宽度", window_width)
        coords_dict = json.loads(content)
        # 解析坐标
        start_x1 = coords_dict["start_x1"]
        start_x2 = coords_dict["start_x2"]
        start_y1 = coords_dict["start_y1"]
        start_y2 = coords_dict["start_y2"]
        end_x1 = coords_dict["end_x1"]
        end_x2 = coords_dict["end_x2"]
        end_y1 = coords_dict["end_y1"]
        end_y2 = coords_dict["end_y2"]
        # 计算中心点
        start_x_center = (start_x1 + start_x2) / 2
        start_y_center = (start_y1 + start_y2) / 2
        end_x_center = (end_x1 + end_x2) / 2
        end_y_center = (end_y1 + end_y2) / 2
        # 屏幕分辨率
        screen_width = int(window_width)
        screen_height = int(content_height)
        # 计算实际屏幕坐标
        start_abs_x = (start_x_center / 1000) * screen_width
        start_abs_y = (start_y_center / 1000) * screen_height
        end_abs_x = (end_x_center / 1000) * screen_width
        end_abs_y = (end_y_center / 1000) * screen_height
        print("起始坐标:", start_abs_x, start_abs_y)
        print("终点坐标:", end_abs_x, end_abs_y)
        return {"start_abs_x": start_abs_x, "start_abs_y": start_abs_y, "end_abs_x":end_abs_x,"end_abs_y":end_abs_y}
    # 滑动-页面滑动的方法入口
    def slide_action(self,step):
        # 网页显示高度
        content_height = self.driver.execute_script("return window.innerHeight")
        viewport_width = self.driver.execute_script("return window.innerWidth")  # 实际可见宽度（修正点1）
        print("实际可见宽度为",viewport_width)
        # 获取浏览器窗口总宽度
        window_size = self.driver.get_window_size()
        window_width = window_size["width"]  # 动态获取窗口宽度
        print("浏览器窗口总宽度", window_width)
        # 屏幕实际内容可视大小
        screen_width = int(window_width)
        screen_height = int(content_height)
        scroll_step = 26  # Chrome单次滚动距离（px）
        # 调用模型
        prompt = f"""
                任务：从用户指令中提取用户要执行上滑，下滑，左滑，还是右滑，并返回滑动距离（半页/全页）
                用户指令：{step}
                要求：
                1.上表示为:ARROW_UP,下表示为:ARROW_DOWN,左表示为:ARROW_LEFT,右表示为:ARROW_RIGHT
                2.全页表示为:1,半页表示为2
                3.指令中如果没有明确为一页，那么都归为半页
                输出要求严格字典：{{"ARROW_UP":1}}
                """
        # 调用大模型API-公司豆包1.6
        response = requests.post(
            "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
            headers={
                "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
                "Content-Type": "application/json"
            },
            json={
                "model": "doubao-seed-1-6-250615",
                "temperature": 0.2,
                "reasoning_effort": "medium",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "text": prompt,
                                "type": "text"
                            }
                        ]
                    }
                ],
                "thinking": {
                    "type": "disabled"
                }
            }
        )
        print("模型返回滑动数据为:", response.json())
        response =  response.json()["choices"][0]["message"]["content"].strip()
        response = json.loads(response)
        print("模型返回滑动精准数据为:", response)
        # 步长
        up_down =max(1, round(screen_height / scroll_step))
        left_right = max(1, round(screen_width / scroll_step))
        print("计算的横向步长为",left_right)
        print("计算的纵向步长为",up_down)
        # 提取返回内容
        key = next(iter(response))
        value = response[key]
        print("要执行的key是",key)
        # 计算点击次数-先计算上下左右，再计算半页全页
        if key in ["ARROW_UP","ARROW_DOWN"]:
            if value == int(1):
                final_count = int(up_down)
            else:
                final_count = int(up_down//2)
        else:
            if value == int(1):
                final_count = int(left_right)
            else:
                final_count = int(left_right//2)
        print("要执行的距离是(次)",final_count)
        actions = ActionChains(self.driver)
        # 模拟按下10次向下箭头键
        key_value = getattr(Keys, key)
        for _ in range(final_count):
            actions.send_keys(key_value).perform()
    # 等待-的方法入口
    def sleeptime_action(self,step):
        # 调用模型
        prompt = f"""
        任务：从等待类型的步骤中提取等待时间，输出纯数字秒数
        用户指令步骤：{step}
        提取规则：
        1.  有明确数字时间：秒级直接取数字；分钟级转换为秒（如"等待2分钟"→120）
        2.  模糊时间词汇：
            - 短时间词（一会、稍等、片刻）→ 3
            - 长时间词（较长、许久）→ 5
        3.  无时间描述（如"等待页面加载"）→ 3
        输出要求：纯数字，无单位、无解释"""
        # 调用大模型API-公司豆包1.6
        response = requests.post(
            "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
            headers={
                "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
                "Content-Type": "application/json"
            },
            json={
                "model": "doubao-seed-1-6-250615",
                "temperature": 0.2,
                "reasoning_effort": "medium",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "text": prompt,
                                "type": "text"
                            }
                        ]
                    }
                ],
                "thinking": {
                    "type": "disabled"
                }
            }
        )
        print("模型返回等待时长数据为:", response.json())
        response = response.json()["choices"][0]["message"]["content"].strip()
        print("模型返回等待时长精准数据为:", response)
        time.sleep(int(response))
        pass
    # 断言-的方法入口
    def ai_assert(self,step):
        # 调用上传模型判断
        verify_value = self.ai_assert_scrrenshot(step)
        # 判断
        self.ai_assert_verify(verify_value)
    # 断言-请求模型
    def ai_assert_scrrenshot(self, step):
        screenshot = self.driver.get_screenshot_as_png()
        screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')
        os.environ["OPENAI_API_KEY"] = "8ceb8471-e3bf-4fe5-9fff-eaa9b37ec08d"
        prompt = f"""
        需求：判断用户断言是否正确并确定类型，需：1. 精准提取核心语义与关键对象；2. 按统一规则对比；3. 输出简洁无冗余。
        步骤1：提取【核心语义】+【关键对象】：
          - 核心语义：用户主张的页面状态；
          - 关键对象：核心语义中“被判断的核心元素”（即判断的聚焦点）；
          （统一规则：若核心语义提及“结果/数值/答案”，关键对象默认是“最终结果/数值”；若提及“显示内容/文本”，关键对象默认是“完整显示文本”）。
        步骤2：明确【实际结果】+【关键对象对应值】：
          - 实际结果：页面真实状态；
          - 关键对象对应值：实际结果中，与“核心语义关键对象”属性匹配的元素（即实际状态中对应关键对象的具体内容）。
        步骤3：判断（基于统一规则）：
          （1）断言类型：
              - 核心语义主张“实际结果的关键对象对应值 = 某目标”→“相等”；
              - 核心语义主张“实际结果的关键对象对应值 ≠ 某目标”→“不相等”；
              - 核心语义涉及“某内容是否存在于页面”→“包含/不包含”。
          （2）结果（仅基于关键对象对应值与目标的对比）：
              - “相等”类型：关键对象对应值与目标一致→正确；否则→错误；
              - “不相等”类型：关键对象对应值与目标不一致→正确；否则→错误。
        用户指令：{step}
        返回格式（严格字典，原因分点简洁）：
        {{"结果":"正确/错误","断言类型":"相等/不相等/包含/不包含","原因":"1.核心语义（关键对象：xxx）：xxx；2.实际结果（关键对象对应值：xxx）：xxx；3.类型依据：xxx；4.结果依据：关键对象对应值与目标一致/不一致"}}
        """
        response = requests.post(
            "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
            headers={
                "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
                "Content-Type": "application/json"
            },
            json={
                "model": "doubao-1-5-ui-tars-250428",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{screenshot_b64}"},
                                "detail": "high"
                            }, {
                                "type": "text",
                                "text": prompt,
                            }
                        ]
                    }
                ]
                ,
                "thinking": {
                    "type": "disabled"
                }
                ,
                "image_pixel_limit": {
                    "max_pixels": 4014080,
                    "min_pixels": 3136
                }
            }
        )
        # print(response.request.body)
        xpath = response.json()
        xpath_value = response.json()["choices"][0]["message"]["content"]
        print("豆包返回值:", xpath)
        print("豆包精准值:", xpath_value)
        return xpath_value
    # 断言-判断是否成立
    def ai_assert_verify(self,verify_value):
        verify_dict = json.loads(verify_value)
        result = verify_dict["结果"]
        if result == "正确":
            pass
        else:
            # assert 1 == 2
            raise ValueError("断言不通过:",verify_dict)  # 抛异常，明确是“断言失败”
    # 判断-这是智能判断的方法入口
    def ai_choice_image(self,step):
        verify_value = self.ai_choice_judge_core(step)
        verify_value = json.loads(verify_value)
        verify_status = verify_value.get("成立状态", "不成立")
        verify_type = verify_value.get("执行类型", "忽略")
        verify_action_value = verify_value.get("执行语义", "忽略")
        # 如果不成立与类型为忽略则pass，其它则调用
        if verify_status=='不成立' or verify_type=='忽略':
            print(f"不成立或忽略：成立状态={verify_status}，执行类型={verify_type}")
            pass
        else:
            print("去调用")
            # 遍历步骤
            if verify_type == "点击":
                self.click_aciton(verify_action_value)
            elif verify_type == "输入":
                self.input_action(verify_action_value)
            elif verify_type == "悬停":
                self.hover_aciton(verify_action_value)
            elif verify_type == "拖拽":
                self.drag_action(verify_action_value)
            elif verify_type == "滑动":
                self.slide_action(verify_action_value)
            elif verify_type == "等待":
                self.sleeptime_action(verify_action_value)
            elif verify_type == "断言":
                self.ai_assert(verify_action_value)
    # 判断-判断步骤核心逻辑
    def ai_choice_judge_core(self, step):
        screenshot = self.driver.get_screenshot_as_png()
        screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')
        prompt = f"""需求：基于传入的页面截图，判断用户判断条件是否成立，提取成立后执行的操作语义及对应执行类型，需：1. 精准拆分判断条件与执行语义；2. 严格基于截图通用识别；3. 输出简洁无冗余、结论明确。
        关键要求：
          1. 必须基于传入截图分析实际结果，禁止返回"需实际查看"等模糊表述，仅能返回"成立"或"不成立"；
          2. 所有识别逻辑通用，不绑定具体页面特征；
          3. 【成立状态判断规则】：成立状态仅由「判断条件」和「截图实际结果」决定，与执行语义（忽略/输入等）无关！
             - 若判断条件主张"某内容存在"（包含类型）：截图中存在该内容→成立，不存在→不成立；
             - 若判断条件主张"某内容不存在"（不包含类型）：截图中不存在该内容→成立，存在→不成立；
             - 禁止因执行语义是"忽略"就篡改成立状态（例：条件是"有弹窗就忽略"，截图无弹窗→条件不成立→成立状态=不成立）
          4. 【执行语义完整保留强制规则】：拆分判断条件与执行语义仅做逻辑分离，**两端语义均需完整保留原句表述，不得删减、缩写、概括任何要素**（如原执行语义是"点击弹窗右下角的同意按钮"，禁止缩写为"点击同意"）
        步骤1：拆分【判断条件】+【执行语义】+【核心对象】+【执行类型】（拆分≠删减，语义完整保留）：
          - 判断条件：用户要验证的页面状态（从完整步骤中拆分，保留完整语义，如"有没有XX弹窗"而非"XX弹窗"）；
          - 执行语义：判断成立后需执行的操作（**完整保留原步骤中执行动作的全部表述，不修改任何文字**，如原步骤是"有弹窗就点击弹窗右下角的同意按钮"，执行语义填"点击弹窗右下角的同意按钮"，无执行动作则填""）；
          - 核心对象：判断条件中"被判断的核心元素"（如"XX弹窗""XX按钮"）；
          - 执行类型：从指定列表选择（点击/输入/长按/拖拽/滑动/等待/断言/忽略），**归类规则及精准判定标准如下**：
            【执行类型精准判定标准（仅可选择以下8类，无例外）】
            1.  点击：主动触发元素的单次按压操作；无法匹配其他类型的执行动作均归为此类，典型执行语义场景为点击弹窗右下角的同意按钮、点击搜索框
            2.  输入：向可输入元素填充文本/数值内容的操作，典型执行语义场景为输入手机号13800138000、输入收货地址
            3.  悬停：鼠标悬浮展开选项或二级菜单的动作，典型场景为悬浮在哪个菜单上，悬浮在习题管理功能上，悬浮在小狗的头上
            4.  拖拽：语义含"拖拽"必须归为此类；将元素从原位置移动到目标位置的主动位移操作，典型执行语义场景为拖拽滑块到右侧完成验证、拖拽文件到上传区
            5.  滑动：页面/控件内的被动位移操作（无明确目标元素拖拽），典型执行语义场景为向上滑动商品列表查看更多、左右滑动切换TAB
            6.  等待：等待页面加载/元素出现/状态变更的操作，典型执行语义场景为等待弹窗加载完成、等待接口返回数据
            7.  断言：验证元素状态/数据是否符合预期的验证操作，典型执行语义场景为断言订单金额为100元、断言按钮状态为禁用
            8.  忽略：无执行动作；执行语义为"忽略""跳过"；无明确执行语义时填此类型，典型执行语义场景为忽略弹窗提示、跳过广告、无操作
            【执行类型归类强制规则】
            1. 基于执行语义本质分析，匹配最贴合类型；
            2.  无法分类的执行动作→统一归为点击；
            3.  无执行语义（如判断成立后无需操作）→执行类型填'忽略'；
            4.  严格区别滑动与拖拽：执行语义含"拖拽"→强制为拖拽；仅描述页面位移→为滑动。
          （统一规则：提及"结果/数值"→核心对象=最终结果/数值；提及"文本"→核心对象=完整显示文本）。
        步骤2：明确【实际结果】+【核心对象对应值】：
          - 实际结果：基于截图的明确结论（核心对象"存在/不存在""是/不是"）；
          - 核心对象对应值：截图中与核心对象匹配的具体状态（如"不存在XX弹窗"）。
        步骤3：判断（基于统一规则）：
          （1）判断类型：
              - 主张"某内容存在"→"包含"；
              - 主张"某内容不存在"→"不包含"；
              - 主张"某值=目标"→"相等"；
              - 主张"某值≠目标"→"不相等"。
          （2）成立状态：
              - 包含类型：核心对象存在→成立，否则→不成立；
              - 不包含类型：核心对象不存在→成立，否则→不成立；
              - 相等/不相等类型：值匹配→成立，否则→不成立。
        用户完整判断步骤：{step}
        返回格式（严格字典，字段不可缺失，成立状态仅能是"成立"或"不成立"，**执行语义必须完整保留原句**）：
        禁止出现"修正后""补充"等修改结论，直接输出最终结果
        {{
            "成立状态":"成立/不成立",
            "判断类型":"相等/不相等/包含/不包含",
            "执行语义":"完整未修改的成立后执行操作语义",
            "执行类型":"从指定列表选择的类型（无执行语义则填'忽略'）",
            "原因":"1.判断条件（核心对象：xxx）：[完整判断条件]；2.实际结果（核心对象对应值：xxx）：基于截图通用识别，xxx；3.类型依据：[执行语义完整表述]符合[执行类型]判定标准；4.成立依据：核心对象对应值符合/不符合判断条件"
        }}"""
        response = requests.post(
            "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
            headers={
                "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
                "Content-Type": "application/json"
            },
            json={
                "model": "doubao-1-5-ui-tars-250428",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{screenshot_b64}"},
                                "detail": "high"
                            },
                            {"type": "text", "text": prompt}
                        ]
                    }
                ],
                "thinking": {"type": "disabled"},
                "image_pixel_limit": {
                    "max_pixels": 4014080,
                    "min_pixels": 3136
                }
            }
        )
        try:
            result = response.json()["choices"][0]["message"]["content"].strip()
            print(f"判断核心逻辑返回：{result}")
            return result  # 返回JSON字符串，后续解析使用
        except Exception as e:
            print(f"判断核心逻辑调用失败：{str(e)}")
            # 异常默认返回不成立
            return json.dumps({
                "成立状态": "不成立",
                "判断类型": "包含",
                "执行语义": "",
                "原因": f"模型调用异常：{str(e)}"
            })
