import os
from flask import Blueprint, request
from core.resp_model import respModel
from extensions import database
# from app import application
from webtest.model.WebKeyWordModel import WebKeyWord  # 请替换为你的ApiModule模型类
from datetime import datetime

# 新增：从数据库重建所有关键字文件的方法
def rebuild_all_keyword_files():
    """从数据库t_web_keyword表重建所有关键字文件"""
    try:
        from app import application
        with application.app_context():
            current_dir = os.path.dirname(os.path.abspath(__file__))
            key_words_dir ="../webtest/keyswords"
            key_words_dir = os.path.join(current_dir, key_words_dir)
            os.makedirs(key_words_dir, exist_ok=True)

            # 查询数据库中所有keyword_value不为空的记录
            keywords = WebKeyWord.query \
                .filter(WebKeyWord.keyword_value.isnot(None)) \
                .filter(WebKeyWord.keyword_value != "") \
                .all()

            # 在 Python 层面过滤纯空白内容
            keywords = [
                kw for kw in keywords
                if kw.keyword_value.strip() != ""
            ]

            total_count = len(keywords)
            success_count = 0
            failed_files = []

            # 遍历记录，逐个生成文件
            for keyword in keywords:
                file_name = keyword.keyword_fun_name
                keyword_value = keyword.keyword_value

                try:
                    with open(f'{key_words_dir}/{file_name}.py', 'w', encoding="utf-8") as f:
                        f.write(keyword_value)
                    success_count += 1
                except Exception as e:
                    print(f"重建文件 {file_name}.py 失败: {str(e)}")
                    failed_files.append(file_name)

            if failed_files:
                print(f"关键字文件重建完成：成功 {success_count} 个，失败 {len(failed_files)} 个")
                print(f"失败的文件: {', '.join(failed_files)}")
            else:
                print(f"所有 {total_count} 个关键字文件重建成功")

            return {
                "success": True,
                "total": total_count,
                "success_count": success_count,
                "failed_files": failed_files
            }

    except Exception as e:
        print(f"重建关键字文件时发生严重错误: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }