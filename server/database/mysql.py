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
        self.player_sql = 'insert into player(user_id,name, position, win_money, private_card, game_id, total_money, money_left, best_cards)' \
                          'values(%s,%s, %s, %s, %s, %s, %s, %s, %s)'
        self.endDate_sql='update batch_room_mapping set end_date=now()  where room_id=%s and batch_count=(select count(1) from game where room_id=%s);'

    def save(self, message):
        # mysql 超时优化
        self.content.ping(reconnect=True)
        game_info = ''.join(message['public_card']), \
                    json.dumps(message['action_history']), \
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), \
                    str(message['room_id'])
        self.cursor.execute(self.game_sql, game_info)
        self.cursor.connection.commit()

        game_id = self.cursor.lastrowid
        for p in range(len(message['position'])):
            player_id = self.trans(message['name'][p])
            player_info = player_id, message['name'][p], message['position'][p], \
                          message['win_money'][p], ''.join(message['player_card'][p]), game_id, \
                          message['total_money'][p], message['money_left'][p], message['best_cards'][p]
            self.cursor.execute(self.player_sql, player_info)
        update_info=str(message['room_id']), \
                    str(message['room_id'])
        self.cursor.execute(self.endDate_sql, update_info)
        self.cursor.connection.commit()

    def trans(self, name):
        player_id = name
        if player_id[-2] == "_" and '0' <= player_id[-1] <= '9':
            player_id = player_id[:-2]
        return player_id

    def end(self):
        self.cursor.close()
        self.content.close()

    def get_agent(self):
        select_sql = 'select name from agent'
        self.cursor.execute(select_sql)
        results = self.cursor.fetchall()
        agents = [result[0] for result in results]
        return agents