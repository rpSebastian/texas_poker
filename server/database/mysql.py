import pymysql
import datetime
import json
from config import cfg


class Mysql:

    def __init__(self):
        self.content = pymysql.Connect(
            host=cfg["database"]["host"],  # mysql的主机ip
            port=cfg["database"]["port"],  # 端口
            user=cfg["database"]["user"],  # 用户名
            passwd=cfg["database"]["password"],  # 数据库密码
            db=cfg["database"]["table"],  # 数据库名
            charset='utf8',  # 字符集
        )
        self.cursor = self.content.cursor()
        self.game_sql = 'insert into game(public_card, action_history, time, room_id) values(%s, %s, %s, %s)'
        self.player_sql = 'insert into player(player_id, name, position, win_money, private_card, game_id, total_money, money_left, best_cards)' \
                          'values(%s, %s, %s, %s, %s, %s, %s, %s, %s)'

    def save(self, message):
        game_info = ''.join(message['public_card']), \
                    json.dumps(message['action_history']), \
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), \
                    str(message['room_id'])
        self.cursor.execute(self.game_sql, game_info)
        game_id = self.cursor.lastrowid
        for p in range(len(message['position'])):
            player_id = self.trans(message['name'][p])
            player_info = player_id, message['name'][p], message['position'][p], \
                          message['win_money'][p], ''.join(message['player_card'][p]), game_id, \
                          message['total_money'][p], message['money_left'][p], message['best_cards'][p]
            self.cursor.execute(self.player_sql, player_info)
        self.cursor.connection.commit()

    def trans(self, name):
        player_id = name
        for bot in cfg['bot'].keys():
            if bot in name:
                player_id = bot
        return player_id

    def end(self):
        self.cursor.close()
        self.content.close()
