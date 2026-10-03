class upload_file:
    def __init__(self, driver):
        self.driver = driver
    def upload_file(self, **kwargs):
        xpath_by = kwargs['定位方式']
        xpath_value = kwargs['目标对象']
        regular_expression = kwargs['正则表达式']
        new_filename = kwargs['新文件名']
        print("定位方式：", xpath_by)
        print("目标对象：", xpath_value)
        print("正则表达式：", regular_expression)
        print("新文件名：", new_filename)
        # 文件目标位置
        current_dir = os.path.dirname(os.path.abspath(__file__))
        target_dir = application.config['UPLOAD_FOLDER']
        target_dir = os.path.abspath(os.path.join(current_dir, target_dir))  # 转为绝对路径
        print("目标目录（target_dir）：", target_dir)
        # 关键：打印目标目录下的所有文件（排查路径是否正确、文件是否存在）
        print("\n===== 目标目录下的所有文件 =====")
        try:
            # 列出目录下的所有条目（文件和文件夹）
            all_items = os.listdir(target_dir)
            for item in all_items:
                item_path = os.path.join(target_dir, item)
                # 区分文件和文件夹，只关注文件
                if os.path.isfile(item_path):
                    print(f"文件：{item}")
                else:
                    print(f"文件夹：{item}（忽略）")
        except FileNotFoundError:
            print(f"错误：目标目录不存在！路径：{target_dir}")
            raise  # 直接抛出异常，因为目录不存在后续无法执行
        print("==============================\n")
        # 1. 用正则表达式查找目标文件（单个）
        matched_files = []
        for file_name in os.listdir(target_dir):
            file_path = os.path.join(target_dir, file_name)
            if os.path.isfile(file_path):
                # 正则匹配（忽略大小写）
                if re.fullmatch(regular_expression, file_name, flags=re.IGNORECASE):
                    matched_files.append(file_path)
        # 2. 校验匹配结果
        if not matched_files:
            raise FileNotFoundError(f"在目录{target_dir}中未找到匹配{regular_expression}的文件")
        if len(matched_files) > 1:
            raise ValueError(f"在目录{target_dir}中找到{len(matched_files)}个匹配文件，仅需1个：{matched_files}")
        original_file_path = matched_files[0]
        print(f"找到原始文件：{original_file_path}")
        # 3. 执行重命名
        new_file_path = os.path.join(target_dir, new_filename)
        # 先判断新文件名是否和原始文件名完全相同（路径一致）
        if original_file_path == new_file_path:
            print("新文件名与原始文件名相同，无需执行重命名操作")
        else:
            # 若新文件已存在，先删除它（避免重命名冲突）
            if os.path.exists(new_file_path):
                os.remove(new_file_path)
                print(f"已删除已存在的目标文件：{new_file_path}")
            # 执行重命名（源文件存在已在前面校验）
            os.rename(original_file_path, new_file_path)
            print(f"文件已从 {original_file_path} 重命名为：{new_file_path}")
        # 4. 上传文件
        element = WebDriverWait(
            self.driver,
            timeout=30,
            poll_frequency=0.5,
            ignored_exceptions=None
        ).until(lambda x: x.find_element(by=xpath_by, value=xpath_value))
        # 4.2 执行JS强制元素可见（解决隐藏导致的不可交互问题）
        self.driver.execute_script("""
            arguments[0].style.display = 'block';

            arguments[0].style.width = '100px';
            arguments[0].style.height = '30px';
            arguments[0].style.opacity = '1';
            arguments[0].style.position = 'static';
            arguments[0].style.zIndex = '9999';
        """, element)
        element.clear()
        element.send_keys(new_file_path)
        print("文件上传操作已执行")
# -*- coding: utf-8 -*-
import difflib
import json
import os
import time
import requests
import warnings
from webtest.tool.webrun.core.globalContext import g_context
warnings.filterwarnings('ignore', message='Unverified HTTPS request')
