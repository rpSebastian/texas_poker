import pymysql

class Mysql:
    def __init__(self):
        self.content = pymysql.Connect(
            host='127.0.0.1',  # mysql的主机ip
            port=3306,  # 端口
            user='xh',  # 用户名
            passwd='0',  # 数据库密码
            db='poker',  # 数据库名
            charset='utf8',  # 字符集
        )
        self.cursor = self.content.cursor()

    # def query(self):
    #     sql = "select * from game;"
    #     self.cursor.execute(sql)
    #     for row in self.cursor.fetchall():
    #         print(row)
    #     print(f"一共查找到：{self.cursor.rowcount}")

    def save(self):
        public_card = '1s2s3s4s6s'
        action_history = '0:c,1:c/0:c,1:c/0:c,1:c/0:c,1:c'
        # sql = 'insert into game(public_card, action_history) values({}, {})'.format(public_card, action_history)
        self.cursor.execute('insert into game(public_card, action_history) values(%s, %s)', (public_card, action_history))
        game_id = self.cursor.lastrowid
        private_card = "'3s4s'"
        name = "'xh'"
        position = 0
        win_money = 20000
        sql = 'insert into player(name, position, win_money, private_card, game_id) values({}, {}, {}, {}, {})'.format(name, position, win_money, private_card, game_id)
        self.cursor.execute(sql)
        self.cursor.connection.commit()

    def end(self):
        self.cursor.close()
        self.content.close()


if __name__ == '__main__':
    mysql = Mysql()
    mysql.save()
    mysql.end()