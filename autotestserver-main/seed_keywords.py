# -*- coding: UTF-8 -*-
"""插入所有操作类型对应的关键字种子数据到数据库"""
import pymysql
import json
from datetime import datetime

conn = pymysql.connect(
    host='localhost', port=3306, user='root', password='123456',
    database='hcdb', charset='utf8mb4'
)
cursor = conn.cursor()

cursor.execute('SELECT keyword_fun_name FROM t_web_keyword')
existing = {r[0] for r in cursor.fetchall()}
print(f'已有 {len(existing)} 个关键字')

now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

keywords = [
    # ====== 浏览器操作 (op_type=1) ======
    (1, '打开URL', 'browser_open_url',
     [{"name": "url", "placeholder": "要打开的URL地址(可省略http前缀)"}]),
    (1, '打开新标签页', 'browser_new_tab',
     [{"name": "url", "placeholder": "新标签页要加载的URL(可选，留空只打开空白页)"}]),
    (1, '切换标签页', 'browser_switch_tab',
     [{"name": "tab_index", "placeholder": "标签页索引(0开始)"},
      {"name": "tab_title", "placeholder": "标签页标题包含文字(与索引二选一)"}]),
    (1, '关闭标签页', 'browser_close_tab', []),
    (1, '刷新页面', 'browser_refresh', []),
    (1, '浏览器后退', 'browser_back', []),
    (1, '浏览器前进', 'browser_forward', []),
    (1, '最大化窗口', 'browser_maximize', []),
    (1, '关闭所有弹窗', 'browser_close_all_popups', []),

    # ====== 元素操作 (op_type=2) ======
    (2, '智能点击', 'element_smart_click',
     [{"name": "定位方式", "placeholder": "xpath/id/css/name/class name"},
      {"name": "目标对象", "placeholder": "元素定位表达式"},
      {"name": "超时时间", "placeholder": "默认30秒"}]),
    (2, '智能输入', 'element_smart_input',
     [{"name": "定位方式", "placeholder": "xpath/id/css/name/class name"},
      {"name": "目标对象", "placeholder": "元素定位表达式"},
      {"name": "输入内容", "placeholder": "要输入的文本"},
      {"name": "是否清空", "placeholder": "true或false"},
      {"name": "是否回车", "placeholder": "true或false"}]),
    (2, '获取元素文本', 'element_get_text',
     [{"name": "定位方式", "placeholder": "xpath/id/css/name/class name"},
      {"name": "目标对象", "placeholder": "元素定位表达式"},
      {"name": "var_name", "placeholder": "存储结果的变量名"}]),
    (2, '获取元素属性', 'element_get_attribute',
     [{"name": "定位方式", "placeholder": "xpath/id/css/name/class name"},
      {"name": "目标对象", "placeholder": "元素定位表达式"},
      {"name": "属性名", "placeholder": "如value/class/href等"},
      {"name": "var_name", "placeholder": "存储结果的变量名"}]),
    (2, '下拉选择', 'element_select_dropdown',
     [{"name": "定位方式", "placeholder": "xpath/id/css"},
      {"name": "目标对象", "placeholder": "下拉框定位表达式"},
      {"name": "选项文本", "placeholder": "要选择的选项文本"},
      {"name": "选项值", "placeholder": "要选择的选项value(与文本二选一)"}]),
    (2, '悬浮元素', 'element_hover',
     [{"name": "定位方式", "placeholder": "xpath/id/css/name/class name"},
      {"name": "目标对象", "placeholder": "元素定位表达式"}]),

    # ====== 坐标操作 (op_type=4) ======
    (4, '坐标点击', 'coordinate_smart_click',
     [{"name": "x", "placeholder": "X坐标(像素)"},
      {"name": "y", "placeholder": "Y坐标(像素)"},
      {"name": "点击次数", "placeholder": "默认1次"},
      {"name": "间隔秒", "placeholder": "多次点击间隔(默认0.2)"}]),
    (4, '坐标悬浮', 'coordinate_smart_hover',
     [{"name": "x", "placeholder": "X坐标(像素)"},
      {"name": "y", "placeholder": "Y坐标(像素)"},
      {"name": "悬浮时间", "placeholder": "悬浮停留秒数(默认1)"}]),
    (4, '坐标输入', 'coordinate_smart_input',
     [{"name": "x", "placeholder": "X坐标(像素)"},
      {"name": "y", "placeholder": "Y坐标(像素)"},
      {"name": "输入内容", "placeholder": "要输入的文字"}]),
    (4, '坐标双击', 'coordinate_double_click',
     [{"name": "x", "placeholder": "X坐标(像素)"},
      {"name": "y", "placeholder": "Y坐标(像素)"}]),
    (4, '坐标右键', 'coordinate_right_click',
     [{"name": "x", "placeholder": "X坐标(像素)"},
      {"name": "y", "placeholder": "Y坐标(像素)"}]),

    # ====== 滑动操作 (op_type=5) ======
    (5, '滚动到元素', 'scroll_to_element_keyword',
     [{"name": "定位方式", "placeholder": "xpath/id/css"},
      {"name": "目标对象", "placeholder": "元素定位表达式"},
      {"name": "对齐方式", "placeholder": "start/center/end(默认center)"}]),
    (5, '按距离滚动', 'scroll_by_distance',
     [{"name": "水平距离", "placeholder": "水平滚动像素(默认0)"},
      {"name": "垂直距离", "placeholder": "垂直滚动像素(默认0)"},
      {"name": "平滑滚动", "placeholder": "true或false(默认true)"}]),
    (5, '滚动到底部', 'scroll_to_bottom',
     [{"name": "平滑滚动", "placeholder": "true或false(默认true)"}]),
    (5, '滚动到顶部', 'scroll_to_top',
     [{"name": "平滑滚动", "placeholder": "true或false(默认true)"}]),
    (5, '元素内滚动', 'scroll_in_element',
     [{"name": "定位方式", "placeholder": "xpath/css"},
      {"name": "目标对象", "placeholder": "容器元素定位"},
      {"name": "水平距离", "placeholder": "默认0"},
      {"name": "垂直距离", "placeholder": "默认100"}]),
    (5, '屏幕滑动', 'swipe_screen',
     [{"name": "起始x", "placeholder": "起始X坐标(默认500)"},
      {"name": "起始y", "placeholder": "起始Y坐标(默认500)"},
      {"name": "目标x", "placeholder": "目标X坐标(默认500)"},
      {"name": "目标y", "placeholder": "目标Y坐标(默认100)"},
      {"name": "滑动时间ms", "placeholder": "持续时间毫秒(默认500)"}]),

    # ====== API请求操作 (op_type=6) ======
    (6, 'GET请求', 'api_get_request',
     [{"name": "url", "placeholder": "请求URL"},
      {"name": "var_name", "placeholder": "存储结果的变量名"},
      {"name": "headers", "placeholder": "请求头JSON字符串"}]),
    (6, 'POST请求', 'api_post_request',
     [{"name": "url", "placeholder": "请求URL"},
      {"name": "body", "placeholder": "请求体JSON字符串"},
      {"name": "var_name", "placeholder": "存储结果的变量名"},
      {"name": "headers", "placeholder": "请求头JSON字符串"}]),
    (6, '提取API响应值', 'api_extract_value',
     [{"name": "源变量", "placeholder": "存储API响应的变量名"},
      {"name": "json路径", "placeholder": "如 data.list.0.name"},
      {"name": "目标变量", "placeholder": "存储提取结果的变量名"}]),

    # ====== 断言操作 (op_type=7) ======
    (7, '断言文本存在', 'assert_text_present',
     [{"name": "断言文本", "placeholder": "页面上应该存在的文本"},
      {"name": "超时时间", "placeholder": "默认30秒"}]),
    (7, '断言元素存在', 'assert_element_exists',
     [{"name": "定位方式", "placeholder": "xpath/id/css等"},
      {"name": "目标对象", "placeholder": "元素定位表达式"},
      {"name": "超时时间", "placeholder": "默认30秒"}]),
    (7, '断言元素可见', 'assert_element_visible',
     [{"name": "定位方式", "placeholder": "xpath/id/css等"},
      {"name": "目标对象", "placeholder": "元素定位表达式"},
      {"name": "超时时间", "placeholder": "默认30秒"}]),
    (7, '断言值相等', 'assert_value_equal',
     [{"name": "预期值", "placeholder": "期望的值"},
      {"name": "变量名", "placeholder": "从全局变量取值的变量名"},
      {"name": "实际值", "placeholder": "直接指定的实际值(与变量名二选一)"}]),
    (7, '断言元素数量', 'assert_element_count',
     [{"name": "定位方式", "placeholder": "xpath/css"},
      {"name": "目标对象", "placeholder": "元素定位表达式"},
      {"name": "期望数量", "placeholder": "期望匹配的元素个数"},
      {"name": "比较方式", "placeholder": "eq/gt/lt/gte/lte(默认eq)"}]),

    # ====== 文件操作 (op_type=8) ======
    (8, '等待文件下载', 'file_wait_download',
     [{"name": "下载目录", "placeholder": "下载目录路径"},
      {"name": "文件名匹配", "placeholder": "文件名通配符如*.xlsx"},
      {"name": "超时时间", "placeholder": "默认60秒"},
      {"name": "var_name", "placeholder": "存储下载文件路径的变量名"}]),
    (8, '文件存在检查', 'file_exists_check',
     [{"name": "文件路径", "placeholder": "要检查的文件路径"},
      {"name": "var_name", "placeholder": "存储结果(true/false)的变量名"}]),
    (8, '文件清理', 'file_cleanup',
     [{"name": "目录", "placeholder": "要清理的目录路径"},
      {"name": "匹配模式", "placeholder": "文件匹配模式如*.xlsx(默认*)"}]),

    # ====== 拖拽操作 (op_type=9) ======
    (9, '拖拽元素', 'drag_and_drop_element',
     [{"name": "源定位方式", "placeholder": "xpath/id/css"},
      {"name": "源目标对象", "placeholder": "被拖拽元素定位"},
      {"name": "目标定位方式", "placeholder": "xpath/id/css"},
      {"name": "目标对象", "placeholder": "目标位置元素定位"}]),
    (9, '按偏移拖拽', 'drag_by_offset',
     [{"name": "定位方式", "placeholder": "xpath/id/css"},
      {"name": "目标对象", "placeholder": "被拖拽元素定位"},
      {"name": "水平偏移", "placeholder": "水平拖拽像素"},
      {"name": "垂直偏移", "placeholder": "垂直拖拽像素"}]),
    (9, '拖拽文件上传', 'drag_file_upload',
     [{"name": "定位方式", "placeholder": "xpath/css"},
      {"name": "目标对象", "placeholder": "拖拽目标区域定位"},
      {"name": "文件路径", "placeholder": "要上传文件的绝对路径"}]),

    # ====== 登录操作 (op_type=10) ======
    (10, '通用表单登录', 'generic_form_login',
     [{"name": "用户名", "placeholder": "登录用户名"},
      {"name": "密码", "placeholder": "登录密码"},
      {"name": "用户名定位方式", "placeholder": "可选，自动检测"},
      {"name": "用户名目标对象", "placeholder": "可选，自动检测"},
      {"name": "密码定位方式", "placeholder": "可选，自动检测"},
      {"name": "密码目标对象", "placeholder": "可选，自动检测"},
      {"name": "登录按钮定位方式", "placeholder": "可选，自动检测"},
      {"name": "登录按钮目标对象", "placeholder": "可选，自动检测"}]),

    # ====== 等待操作 (op_type=11) ======
    (11, '等待元素可见', 'wait_element_visible',
     [{"name": "定位方式", "placeholder": "xpath/id/css/name等"},
      {"name": "目标对象", "placeholder": "元素定位表达式"},
      {"name": "超时时间", "placeholder": "默认30秒"}]),
    (11, '等待元素消失', 'wait_element_disappear',
     [{"name": "定位方式", "placeholder": "xpath/id/css/name等"},
      {"name": "目标对象", "placeholder": "元素定位表达式"},
      {"name": "超时时间", "placeholder": "默认30秒"}]),
    (11, '等待页面加载', 'wait_page_ready_keyword',
     [{"name": "超时时间", "placeholder": "默认30秒"}]),
    (11, '固定等待', 'wait_fixed_seconds',
     [{"name": "等待秒数", "placeholder": "等待的秒数(如1.5)"}]),
    (11, '等待文本出现', 'wait_text_present',
     [{"name": "等待文本", "placeholder": "等待出现的文本内容"},
      {"name": "超时时间", "placeholder": "默认30秒"}]),
    (11, '等待URL包含', 'wait_url_contains',
     [{"name": "url包含", "placeholder": "URL应包含的字符串"},
      {"name": "超时时间", "placeholder": "默认30秒"}]),
    (11, '等待元素数量', 'wait_element_count',
     [{"name": "定位方式", "placeholder": "xpath/css"},
      {"name": "目标对象", "placeholder": "元素定位表达式"},
      {"name": "期望数量", "placeholder": "至少出现N个元素"},
      {"name": "超时时间", "placeholder": "默认30秒"}]),
]

inserted = 0
skipped = 0
for op_type_id, name, fun_name, param_desc in keywords:
    if fun_name in existing:
        print(f'  [SKIP] {name} ({fun_name}) - 已存在')
        skipped += 1
        continue
    desc_json = json.dumps(param_desc, ensure_ascii=False)
    cursor.execute(
        'INSERT INTO t_web_keyword (name, operation_type_id, keyword_fun_name, keyword_desc, keyword_value, is_enabled, create_time) VALUES (%s, %s, %s, %s, %s, %s, %s)',
        (name, op_type_id, fun_name, desc_json, '', 'true', now)
    )
    inserted += 1
    print(f'  [INSERT] {name} ({fun_name}) -> op_type={op_type_id}')

conn.commit()

cursor.execute('SELECT COUNT(*) FROM t_web_keyword')
total = cursor.fetchone()[0]
cursor.close()
conn.close()

print(f'\n成功插入 {inserted} 个新关键字，跳过 {skipped} 个已存在，数据库共 {total} 个关键字')
