import pymysql
import datetime


class Mysql:

    def __init__(self):
        self.content = pymysql.Connect(
            host='a.xuhang.ink',  # mysql的主机ip
            port=3306,  # 端口
            user='xh',  # 用户名
            passwd='0',  # 数据库密码
            db='poker2',  # 数据库名
            charset='utf8',  # 字符集
        )
        self.cursor = self.content.cursor()
        self.game_sql = 'insert into game(public_card, action_history, time) values(%s, %s, %s)'
        self.player_sql = 'insert into player(name, position, win_money, private_card, game_id)' \
                          'values(%s, %s, %s, %s, %s)'

    def save(self, message):
        game_info = ''.join(message['public_card']), \
                    '/'.join(','.join(p) for p in message['action_history']), \
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(self.game_sql, game_info)
        game_id = self.cursor.lastrowid
        for p in range(len(message['position'])):
            player_info = message['name'][p], message['position'][p], \
                          message['win_money'][p], ''.join(message['player_card'][p]), game_id
            self.cursor.execute(self.player_sql, player_info)
        self.cursor.connection.commit()

    def end(self):
        self.cursor.close()
        self.content.close()
