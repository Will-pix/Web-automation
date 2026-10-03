def query_all(db_config, sql):
    import pymysql
    from pymysql import cursors
    config = {  # 数据库配置
        "host": '127.0.0.1',
        "user": 'oo',
        "password": '123456',
        "port": 3306,
        "db": 'myuser',
        "cursorclass": cursors.DictCursor}
    config.update(db_config)
    con = pymysql.connect(**config)
    cur = con.cursor()
    cur.execute(sql)
    result = cur.fetchall()
    cur.close()
    con.close()
    return result