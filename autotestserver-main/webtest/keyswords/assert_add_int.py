from webtest.tool.webrun.core.globalContext import g_context

class assert_add_int:
    def __init__(self, driver):
        self.driver = driver

    def assert_add_int(self, **kwargs):
        # 获取变量名（字符串键）
        var1_key = kwargs["变量1"]
        var2_value = int(kwargs["变量2"])  # 已转换为整数
        var3_key = kwargs["变量3"]

        # 从全局变量获取值，并转换为整数
        value1 = int(g_context().get_dict(var1_key))  # 字符串转整数
        value3 = int(g_context().get_dict(var3_key))  # 字符串转整数

        #打印计算过程和结果
        print(f"====== 计算过程=======")
        print(f"变量1键名:{var1_key},转换为整数:{value1}")
        print(f"变量2值:{var2_value}(整数)")
        print(f"变量3键名:{var3_key},转换为整数:{value3}")
        print(f"计算式:{value1} +{var2_value}={value1+ var2_value}")
        print(f"预期结果:{value3}")
        print(f"是否相等:{value1 +var2_value== value3}")
        print(f"=====================")


        # 断言：整数相加是否等于目标值
        assert value1 + var2_value == value3, \
            f"断言失败：{value1} + {var2_value} 不等于 {value3}"