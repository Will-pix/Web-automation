def aesEnrcypt(key, data):
    from apitest.tool.apirunner.extend.crypto.aes_enrcypt import EncryptData

    """ AES 加密封装 """
    print("start=========")
    print("加密原文:", data)
    print("加密key:", key)
    eg = EncryptData(key)  # 这里密钥的长度必须是16的倍数
    res = eg.encrypt(str(data))
    print("密文:", res)
    return res


def sql_exec(type, db_config, sql):
    print("start=========")
    print("连接数据库:", db_config)
    print("执行SQL:", sql)
    result = None
    if type == 'mysql':
        from apitest.tool.apirunner.extend.database.SqlByMysql import query_all
        result = query_all(db_config, sql)
    print("SQL执行结果：", result)
    print("end=========")
    return result
