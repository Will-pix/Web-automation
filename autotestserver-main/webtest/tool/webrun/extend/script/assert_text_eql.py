# -*- coding: utf-8 -*-
# @Time : 2024/6/4 16:45
# @Author : Hami
#  注意事项：
#  1. 文件名、类名、 方法名 必须一致
#  2. 必须有对应的构造方法，实例化的时候 必须传对应driver过来

class assert_text_eql:

    def __init__(self, driver):
        self.driver = driver

    def assert_text_eql(self, **kwargs):
        # 预期值
        target = kwargs["数据内容"]
        # 当前值
        current = self.driver.find_element(kwargs["定位方式"], kwargs["目标对象"]).text
        print(f"判断是否相等,{target} - {current}")
        assert current == target
