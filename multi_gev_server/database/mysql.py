import pymysql
import datetime
import json
from utils.config import cfg


class DataCollector():
    def __init__(self):
        self.data_list = []
        self.counter = 0

    def __len__(self):
        return len(self.data_list)

    def save_game_info(self, game_info): 
        info = dict(game_info=game_info, players_info=[])
        self.data_list.append(info)

    def save_player_info(self, player_info):
        self.data_list[-1]["players_info"].append(player_info)

    def get_all_game_info(self):
        all_game_info = []
        for info in self.data_list:
            all_game_info.append(info["game_info"])
        return all_game_info

    def get_all_player_info(self):
        all_player_info = []
        for info in self.data_list:
            for player_info in info["players_info"]:
                all_player_info.append(player_info)
        return all_player_info

    def save_game_id(self, first_game_id):
        for i, info in enumerate(self.data_list):
            for player_info in info["players_info"]:
                player_info[0] = first_game_id + i

    def clear(self):
        del self.data_list
        self.data_list = []

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
        self.player_sql = 'insert into player(game_id, user_id,name, position, win_money, private_card, total_money, money_left, best_cards, room_id)' \
                          'values(%s,%s, %s, %s, %s, %s, %s, %s, %s, %s)'
        self.data_clt = DataCollector()

    def save(self, message):
        # mysql 超时优化
        self.content.ping(reconnect=True)
        game_info = ''.join(message['public_card']), \
                    json.dumps(message['action_history']), \
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), \
                    str(message['room_id'])
        self.data_clt.save_game_info(game_info)

        for p in range(len(message['position'])):
            player_id = self.trans(message['name'][p])
            player_info = [0, player_id, message['name'][p], message['position'][p], \
                          message['win_money'][p], ''.join(message['player_card'][p]), \
                          message['total_money'][p], message['money_left'][p], message['best_cards'][p], message['room_id']]
            self.data_clt.save_player_info(player_info)
        
    def save_data(self):
        if len(self.data_clt) == 0:
            return
        all_game_info = self.data_clt.get_all_game_info()
        self.cursor.executemany(self.game_sql, all_game_info)
        self.cursor.connection.commit()
        first_game_id = self.cursor.lastrowid
        self.data_clt.save_game_id(first_game_id)
        all_player_info = self.data_clt.get_all_player_info()
        self.cursor.executemany(self.player_sql, all_player_info)
        self.cursor.connection.commit()
        self.data_clt.clear()

    def trans(self, name):
        agents = self.get_agent()
        player_id = name
        if "1" <= name[-1] <= "9" and name[:-1] in agents:
            player_id = name[:-1]
        return player_id

    def end(self):
        self.cursor.close()
        self.content.close()

    def get_agent(self):
        self.content.ping(reconnect=True)
        select_sql = 'select name from agent'
        self.cursor.execute(select_sql)
        results = self.cursor.fetchall()
        agents = [result[0] for result in results]
        self.cursor.connection.commit()
        return agents
