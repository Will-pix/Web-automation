class g_context(object):
    _dic = {}  # 内置属性，外部不可修改
    """
    _dic 属性：这是一个类属性，作为全局上下文的存储容器，本质是一个字典，用于存储所有的全局变量。初始时为空字典，后续可以通过 set_dict 或 set_by_dict 方法向其中添加或更新键值对。
    set_dict 方法：该方法接受两个参数 key 和 value，用于向全局上下文中添加或更新单个键值对。具体实现是将 key 和 value 存储到 _dic 字典中。
    get_dict 方法：该方法接受一个参数 key，用于从全局上下文中获取指定键的值。如果 key 存在于 _dic 字典中，则返回对应的值；否则会抛出 KeyError 异常。
    set_by_dict 方法：该方法接受一个参数 dic，用于将传入的字典 dic 中的所有键值对更新到 _dic 中。如果有相同的键，会用传入字典的值覆盖原有的值。这是通过调用字典的 update 方法实现的。
    show_dict 方法：该方法用于返回当前全局上下文的字典 _dic，方便查看全局上下文中存储的所有键值对。
    """
    # 插入/修改一个键值
    def set_dict(self, key, value):  # 函数 -- PI*r*r
        self._dic[key] = value

    # 根据key查询一个变量
    def get_dict(self, key):
        return self._dic[key]

    # 根据字典插入/修改
    def set_by_dict(self, dic):
        self._dic.update(dic)

    # 获取全部存储的变量
    def show_dict(self):
        return self._dic

