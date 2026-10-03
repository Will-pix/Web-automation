import operator


def assert_exec(type, target_value, assert_value):
    """
    type： 断言类型
    target_value： 接口返回值
    assert_value： 预期值
    """
    if type == "exists":  # 存在
        return target_value != False
    elif type == 'contains':  # 包含
        return target_value.__contains__(assert_value)
    elif type == 'equals':  # 相同
        return str(target_value) == assert_value
    else: # 数学计算
        return getattr(operator, type)(float(target_value), float(assert_value))