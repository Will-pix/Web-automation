import requests
import json
import sys
import getpass

LOCAL_URL = "http://127.0.0.1:5000/api"
COMPANY_URL = "https://autotestweb-test.yc345.tv/api"
BASE_URL = LOCAL_URL  # 将在 main 中初始化

def select_environment():
    """选择运行环境"""
    print("\n[STEP 0] 环境配置")
    print(f"1. 本地环境 ({LOCAL_URL})")
    print(f"2. 公司环境 ({COMPANY_URL})")
    choice = input("请输入序号选择 (默认1): ").strip() or "1"
    url = COMPANY_URL if choice == "2" else LOCAL_URL
    print(f"已选择环境: {url}")
    return url

def get_token_by_login():
    """通过账号密码登录获取Token"""
    print("\n[STEP 1] 登录")
    username = input("请输入用户名 (默认: admin): ").strip() or "admin"
    password = getpass.getpass("请输入密码 (默认: 123456): ").strip() or "123456"

    try:
        resp = requests.post(f"{BASE_URL}/login", json={
            "username": username,
            "password": password
        })
        if resp.status_code == 200 and resp.json().get("code") == 200:
            token = resp.json()["data"]["token"]
            print("登录成功！")
            return token
        else:
            print(f"登录失败: {resp.text}")
            return None
    except Exception as e:
        print(f"登录异常: {e}")
        return None

def find_case_by_id(headers, case_id):
    """通过ID查找/验证测试用例"""
    print(f"\n[STEP 2] 验证用例 ID: {case_id}")
    try:
        resp = requests.get(f"{BASE_URL}/WebInfo/queryById?id={case_id}", headers=headers)
        if resp.status_code == 200 and resp.json().get("code") == 200:
            data = resp.json().get("data", {})
            if data and data.get("id") == int(case_id):
                 print(f"验证成功: 用例名称 '{data.get('case_name')}'")
                 return int(case_id)
            else:
                 print("验证失败: 未找到该ID对应的详细信息。")
                 return None
        else:
             print(f"查找失败: {resp.text}")
             return None
    except Exception as e:
        print(f"查找异常: {e}")
        return None

def find_or_create_keyword(headers, keyword_name="AI融合视觉"):
    """查找关键字ID，如果需要可以在这里扩展创建逻辑"""
    print(f"\n[STEP 3] 查找关键字: {keyword_name}")
    # 这里为了简便，先尝试通过 queryByPage 查找
    # 注意：本地代码中 WebKeyWordController 的 queryByPage 支持按 name 模糊搜索
    try:
        payload = {
            "page": 1,
            "pageSize": 10,
            "name": keyword_name
        }
        resp = requests.post(f"{BASE_URL}/WebKeyWord/queryByPage", json=payload, headers=headers)
        if resp.status_code == 200 and resp.json().get("code") == 200:
            data_list = resp.json().get("data", [])
            for item in data_list:
                if item['name'] == keyword_name:
                    print(f"找到关键字 ID: {item['id']}")
                    return item['id']
            
            print(f"未找到精确匹配 '{keyword_name}' 的关键字。")
            create_choice = input("是否尝试创建该关键字? (y/n) [默认y]: ").strip().lower() or 'y'
            if create_choice == 'y':
                return create_keyword(headers, keyword_name)
            return None
        else:
            print(f"查找关键字失败: {resp.text}")
            return None
    except Exception as e:
        print(f"查找关键字异常: {e}")
        return None

def create_keyword(headers, keyword_name):
    """创建关键字"""
    print(f"正在尝试创建关键字: {keyword_name}...")
    # 需要先找到 '告警' 操作类型的ID
    op_type_id = 999 
    try:
        # 简单查一下所有 OperationType
        # 注意：这里假设 WebOperationType 有 queryAll 接口
        # 实际上代码里有 queryAllKeyWordList 但那个返回树状结构
        # 我们可以尝试直接硬编码或者让用户输入
        # 为了稳妥，这里先假设 ID=1 或者让用户输入，或者尝试查询
        # 如果是本地环境，我会帮你创建好，如果是公司环境，可能需要你自己确认 ID
        
        # 简化逻辑：这里假设本地环境我已经帮你建好了
        # 如果是在公司环境运行，建议手动输入 ID 以防万一
        op_id_input = input("请输入'告警'操作类型的ID (如果不知道，请回车跳过尝试使用默认值): ").strip()
        if op_id_input:
            op_type_id = int(op_id_input)
        
        payload = {
            "name": keyword_name,
            "keyword_fun_name": "ai_merge_vision", # 假设的方法名
            "keyword_desc": "AI融合视觉步骤",
            "operation_type_id": op_type_id,
            "keyword_value": "pass", # 占位符
            "is_enabled": "1" # 字符串或数字？看模型定义是String
        }

        resp = requests.post(f"{BASE_URL}/WebKeyWord/insert", json=payload, headers=headers)
        if resp.status_code == 200 and resp.json().get("code") == 200:
            new_id = resp.json().get("data", {}).get("id")
            print(f"创建成功，ID: {new_id}")
            return new_id
        else:
            print(f"创建关键字失败: {resp.text}")
            manual_id = input("创建失败，请输入现有的关键字ID以继续: ").strip()
            if manual_id: return int(manual_id)
            return None
    except Exception as e:
        print(f"创建关键字异常: {e}")
        return None

def batch_import_steps(headers, web_info_id, keyword_id, text_content):
    """批量导入步骤"""
    print(f"\n[STEP 4] 开始批量导入")
    lines = text_content.strip().split('\n')
    valid_lines = [line.strip() for line in lines if line.strip()]
    
    total = len(valid_lines)
    print(f"共解析出 {total} 行有效文本，准备导入...")
    
    success_count = 0
    
    for idx, line in enumerate(valid_lines, 1):
        step_desc = f"步骤{idx}"
        
        # 构建请求数据
        payload = {
            "web_info_id": web_info_id,
            "key_word_id": keyword_id,
            "step_desc": step_desc,
            # 关键修正: ref_variable 必须是 JSON 字符串，且必须包含 ai_step 参数
            "ref_variable": json.dumps({"ai_step": line}, ensure_ascii=False), 
            "run_order": idx * 10, # 间隔10，方便后续插入
            "is_enabled": True,
            "step_value_pass": 2, # "告警" 状态 (由用户确认)
        }
        
        # 已确认: 告警对应字段 step_value_pass = 2
        # payload["exception_handling"] = "告警" # 旧的猜测，删除 

        try:
            resp = requests.post(f"{BASE_URL}/WebInfoStep/insert", json=payload, headers=headers)
            if resp.status_code == 200 and resp.json().get("code") == 200:
                print(f"[{idx}/{total}] 导入成功: {step_desc}")
                success_count += 1
            else:
                print(f"[{idx}/{total}] 导入失败: {resp.text}")
        except Exception as e:
            print(f"[{idx}/{total}] 请求异常: {e}")
            
    print(f"\n导入完成！成功: {success_count}/{total}")

def main():
    global BASE_URL
    print("=== Web自动化平台 批量导入工具 (Batch Import Client) ===\n")
    
    # 0. 选择环境
    BASE_URL = select_environment()
    
    # 1. 获取 Token
    print("请选择登录方式:")
    print("1. 账号密码登录 (自动获取Token)")
    print("2. 手动输入 Token")
    mode = input("请输入序号 (默认1): ").strip() or "1"
    
    token = None
    if mode == "1":
        token = get_token_by_login()
    else:
        token = input("请输入 Bearer Token (不含'Bearer '前缀): ").strip()
    
    if not token:
        print("未获取到有效Token，程序退出。")
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 2. 查找目标用例
    case_input = input("\n请输入要做导入的目标【用例集合ID】(例如 261): ").strip()
    if not case_input:
        print("ID不能为空。")
        return
    
    # 尝试解析 ID
    try:
        target_case_id = int(case_input)
    except ValueError:
        print("请输入有效的数字ID。")
        return

    web_info_id = find_case_by_id(headers, target_case_id)
    if not web_info_id:
        return

    # 3. 查找/确认关键字
    keyword_id = find_or_create_keyword(headers)
    if not keyword_id:
        # 如果自动找不到，允许手动兜底
        manual_id = input("\n无法自动确定关键字ID，请手动输入关键字ID (输入 q 退出): ").strip()
        if manual_id.lower() == 'q':
            return
        keyword_id = int(manual_id)

    # 4. 输入文本内容
    print("\n请输入要导入的大段文本 (输入完后按 Ctrl+Z (Windows) 或 Ctrl+D (Mac/Linux) + 回车结束输入):")
    # 支持多行输入
    try:
        lines = sys.stdin.readlines()
        text_content = "".join(lines)
    except KeyboardInterrupt:
        return

    if not text_content.strip():
        print("内容为空，取消导入。")
        return

    # 5. 执行导入
    confirm = input(f"\n即将向用例ID {web_info_id} 导入 {len(text_content.strip().splitlines())} 条数据，关键字ID为 {keyword_id}，确认执行? (y/n): ")
    if confirm.lower() == 'y':
        batch_import_steps(headers, web_info_id, keyword_id, text_content)
    else:
        print("已取消。")

if __name__ == "__main__":
    main()
