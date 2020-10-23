import os
import sys

import pymysql
import datetime
import json

ia = "OpenStack"
thu = "YangJun"
ict = "LiShuoKai"

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
    
    def query(self, sql, info):
        self.cursor.execute(sql, info)
        results = self.cursor.fetchall()
        self.cursor.connection.commit()
        return results

    def get_room_id(self, players):
        sql = "SELECT room_id FROM batch_ai_validate as a, validate_room_mapping as b WHERE a.batch_id = b.batch_id and a.bot_list = %s"
        info = ','.join(players)
        self.cursor.execute(sql, info)
        result = self.cursor.fetchall()
        room_ids = [row[0] for row in result]
        return room_ids

    def lookup(self, players):
        room_ids = self.get_room_id(players)
        for player in players:
            game_sql = "select count(*), sum(win_money) from player where room_id = %s and name = %s"
            count, money = 0, 0
            for room_id in room_ids:
                game_info = str(room_id), player
                result = self.query(game_sql, game_info)[0]
                if result[0] > 0:
                    count += result[0]
                    money += result[1]
            print(players, player, count, money, money / count)

    def get_game_id(self, room_ids, main_player):
        sql = "select game_id from player where room_id in %s and name = %s"
        info = room_ids, main_player
        result = self.query(sql, info)
        game_ids = [row[0] for row in result]
        return game_ids

    def export_battle_data(self, players, main_player):
        room_ids = self.get_room_id(players)
        game_ids = self.get_game_id(room_ids, main_player)
        sql = "Select game.room_id, game.public_card, player.private_card, player.win_money, player.name, game.action_history from player, game where game.game_id=player.game_id and player.game_id in %s"
        info = (game_ids[:2], )
        result = self.query(sql, info)
        print(result[0])


    def end(self):
        self.cursor.close()
        self.content.close()

# Mysql().lookup([ia, thu])
# Mysql().lookup([ia, ict])
# Mysql().lookup([thu, ict])
Mysql().export_battle_data([ia, thu], thu)