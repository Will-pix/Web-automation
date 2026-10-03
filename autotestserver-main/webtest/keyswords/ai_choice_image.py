import base64
import json
import os
import requests
import time
from ai_input_image import ai_input_image as AiInputImage
from ai_click_image import ai_click_image
from ai_hover_image import ai_hover_image
from ai_drag_drop import ai_drag_drop
# from ai_action_merge import slide_action, sleeptime_action, ai_assert
from ai_action_merge import ai_action_merge
from webtest.keyswords.ai_runtime import get_runtime_ai_settings

class ai_choice_image:
    def __init__(self, driver):
        self.driver = driver
        # ai_action_merge = ai_action_merge()

    # 方法入口
    def ai_choice_image(self, **kwargs):
        ai_step = kwargs["ai_step"]
        print("接收值:", ai_step)
        os.environ["OPENAI_API_KEY"] = get_runtime_ai_settings()["api_key"]  # 替换为实际密钥
        # 调用解析语义
        action_step = self.ai_assert_Analysis_aciton(ai_step)
        # 调用上传模型判断
        verify_value = self.ai_choice_judge_core(action_step)
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
                ai_click_image(self.driver).ai_click_image(ai_step=verify_action_value)
            elif verify_type == "输入":
                AiInputImage(self.driver).ai_input_image(ai_step=verify_action_value)
            elif verify_type == "悬停":
                ai_hover_image(self.driver).ai_hover_image(ai_step=verify_action_value)
            elif verify_type == "拖拽":
                ai_drag_drop(self.driver).ai_drag_drop(ai_step=verify_action_value)
            elif verify_type == "滑动":
                ai_action_merge.slide_action(self.driver, ai_step=verify_action_value)
            elif verify_type == "等待":
                ai_action_merge.sleeptime_action(self.driver, ai_step=verify_action_value)
            elif verify_type == "断言":
                ai_action_merge.ai_assert(self.driver, ai_step=verify_action_value)

    # 使用模型语义分析判断
    def ai_assert_Analysis_aciton(self, ai_step):
        os.environ["OPENAI_API_KEY"] = get_runtime_ai_settings()["api_key"]
        prompt = f"""
        任务：从用户指令中分析用户想要执行的步骤数量及每个步骤要执行的类型

        用户指令：
        {ai_step}

        分析要求：
        1. 分析用户总要执行的步骤，进行文本切割
        2. 根据步骤分析用户要操作的类型，并归类，类型仅有八个，点击，输入，悬停，拖拽，滑动，等待，断言，判断，如果无法分类都归为点击
        3. 保留完整语义（如"今天天气"而非"今天"）,只进行拆分步骤和补充类型
        4.【判断类型识别专项规则】：
            - 若某段内容同时包含「条件逻辑」和「执行逻辑」（即“满足XX条件，就执行XX操作”的结构），无论是否包含“是否/有没有/检查/判断/如果”等关键词，该内容均为「判断步骤的完整语义」，必须作为一个独立步骤，不拆分内部逻辑；
            - 常见条件逻辑标识（仅为提示，不局限于此）：如果、若、要是、假如、是否、有没有、检查、判断；
            - 常见执行逻辑标识（仅为提示，不局限于此）：就、则、便、才、有就、没有就；
            - 满足上述结构的步骤，类型强制归为“判断”。
        5. 多执行动作分割要求：判断步骤仅能带一个执行动作，多余执行动作（用“并/且/同时”连接）需分割为独立普通步骤（类型匹配动作本身）。
        输出要求-列表套字典：[{{"order":顺序,"type":"类型","step":"切割的步骤信息"}}]
        """
        # 调用大模型API-豆包1.6
        response = requests.post(
            f"{get_runtime_ai_settings()['api_base']}/chat/completions",
            headers={
                "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
                "Content-Type": "application/json"
            },
            json={
                "model": get_runtime_ai_settings()["text_model"],
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


        # 获取当前页面截图

        # 发送模型截图与描述判断条件是否成立（如果成立则返回true与应该做的，如果不成立则返回false）需要设定规则

        # 进入执行（如果满足则执行，不满足则pass）

    # 根据截图和语义来进行判断是否成立
    # 新增：判断步骤核心逻辑（参考断言方法，仅改Prompt和返回格式适配）
    def ai_choice_judge_core(self, step):
        screenshot = self.driver.get_screenshot_as_png()
        screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')
        prompt = f"""
                 需求：基于传入的页面截图，判断用户判断条件是否成立，提取成立后执行的操作语义及对应执行类型，需：1. 精准拆分判断条件与执行语义；2. 严格基于截图通用识别；3. 输出简洁无冗余、结论明确。
                 关键要求：
                   1. 必须基于传入截图分析实际结果，禁止返回“需实际查看”等模糊表述，仅能返回“成立”或“不成立”；
                   2. 所有识别逻辑通用，不绑定具体页面特征；
                   3. 【成立状态判断规则】：成立状态仅由「判断条件」和「截图实际结果」决定，与执行语义（忽略/输入等）无关！
                      - 若判断条件主张“某内容存在”（包含类型）：截图中存在该内容→成立，不存在→不成立；
                      - 若判断条件主张“某内容不存在”（不包含类型）：截图中不存在该内容→成立，存在→不成立；
                      - 禁止因执行语义是“忽略”就篡改成立状态（例：条件是“有弹窗就忽略”，截图无弹窗→条件不成立→成立状态=不成立）。
                 步骤1：拆分【判断条件】+【执行语义】+【核心对象】+【执行类型】：
                   - 判断条件：用户要验证的页面状态（从完整步骤中拆分，如“有没有XX元素”）；
                   - 执行语义：判断成立后需执行的操作（如“点同意”“忽略”，无则填""）；
                   - 核心对象：判断条件中“被判断的核心元素”（如“XX弹窗”“XX按钮”）；
                   - 执行类型：从指定列表选择（点击/输入/悬停/拖拽/滑动/等待/断言/忽略），归类规则：
                     1. 基于执行语义本质分析，匹配最贴合类型；
                     2. 无法分类→点击；
                     3. 无执行语义→执行类型填'忽略'。
                   （统一规则：提及“结果/数值”→核心对象=最终结果/数值；提及“文本”→核心对象=完整显示文本）。
                 步骤2：明确【实际结果】+【核心对象对应值】：
                   - 实际结果：基于截图的明确结论（核心对象“存在/不存在”“是/不是”）；
                   - 核心对象对应值：截图中与核心对象匹配的具体状态（如“不存在XX弹窗”）。
                 步骤3：判断（基于统一规则）：
                   （1）判断类型：
                       - 主张“某内容存在”→“包含”；
                       - 主张“某内容不存在”→“不包含”；
                       - 主张“某值=目标”→“相等”；
                       - 主张“某值≠目标”→“不相等”。
                   （2）成立状态：
                       - 包含类型：核心对象存在→成立，否则→不成立；
                       - 不包含类型：核心对象不存在→成立，否则→不成立；
                       - 相等/不相等类型：值匹配→成立，否则→不成立。

                 用户完整判断步骤：{step}
                 返回格式（严格字典，字段不可缺失，成立状态仅能是“成立”或“不成立”）：
                 禁止出现“修正后”“补充”等修改结论，直接输出最终结果
                 {{
                     "成立状态":"成立/不成立",
                     "判断类型":"相等/不相等/包含/不包含",
                     "执行语义":"拆分出的成立后操作语义",
                     "执行类型":"从指定列表选择的类型（无执行语义则填'忽略'）",
                     "原因":"1.判断条件（核心对象：xxx）：xxx；2.实际结果（核心对象对应值：xxx）：基于截图通用识别，xxx；3.类型依据：xxx；4.成立依据：核心对象对应值符合/不符合判断条件"
                 }}
                 """
        response = requests.post(
            f"{get_runtime_ai_settings()['api_base']}/chat/completions",
            headers={
                "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
                "Content-Type": "application/json"
            },
            json={
                "model": get_runtime_ai_settings()["vision_model"],
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

