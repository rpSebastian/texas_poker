import pymysql


class Mysql:

    def __init__(self):
        self.content = pymysql.Connect(
            host="172.18.40.65",  # mysql的主机ip
            port=3306,  # 端口
            user="root",  # 用户名
            passwd="root",  # 数据库密码
            db="poker",  # 数据库名
            charset='utf8',  # 字符集
        )
        self.cursor = self.content.cursor()

    def query(self, sql):
        self.content.ping(reconnect=True)
        try:
            self.cursor.execute(sql)
            self.cursor.connection.commit()
            result = self.cursor.fetchall()
        except pymysql.err.ProgrammingError:
            print("请检查sql语句: {}".format(sql))
            result = None
        return result