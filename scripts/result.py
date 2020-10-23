import pymysql
import pandas as pd
import json
from collections import defaultdict

def main():
    name = "TestAI vs nudt"
    # name = "Hit_6p_test"
    Mysql().lookup(name) 
    Mysql().battle_history(name)


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

    def lookup(self, battle_name):
        game_sql = 'select bot_list from batch_ai_validate where batch_name like "{}%"'.format(battle_name)
        self.cursor.execute(game_sql)
        result = self.cursor.fetchall()
        bots = result[0][0].split(',')

        table = pd.DataFrame(columns=['AI名字', '总局数', '累积收益筹码', '场均收益筹码', '0.95置信区间'])

        for bot in bots:
            game_sql = (
                'SELECT count(*) AS 总局数, sum( win_money ) AS 总赢钱, Round( sum( win_money ) / count(*) , 2 ) AS "mbb/h", Round( STD( win_money ) * 10, 2 ) AS 标准差, '
                'Round( 1.96 * STD( win_money )/ POWER( count(*), 1 / 2 ) , 2 ) AS "0.95置信区间范围" FROM player ' 
                'WHERE room_id IN (select room_id from validate_room_mapping where batch_name like "{}%" '
        	    'and name = "{}")'
            ).format(battle_name, bot)
            self.cursor.execute(game_sql)
            self.cursor.connection.commit()
            result = self.cursor.fetchall()[0]
            table.loc[table.shape[0]] = [bot, result[0], result[1], result[2], result[4]]
        print(table)
        writer = pd.ExcelWriter('{}_stat.xlsx'.format(battle_name))  
        table.to_excel(writer,float_format='%.5f')
        writer.save()

    def transpose(self, action_history):
        def f(x):
            if x == "call":
                return "c"
            if x == "check":
                return "c"
            if x == "fold":
                return "f"
            return x
        game_all = []
        for one_round in action_history:
            round_all = []
            for one_action in one_round:
                action = str(one_action["position"]) + ":" + f(str(one_action["action"]))
                round_all.append(action)
            round_all = ','.join(round_all)
            game_all.append(round_all)
        game_all = '/'.join(game_all)
        return game_all

    def battle_history(self, battle_name, save_file=True):
        history = {}
        game_sql = 'SELECT * FROM game WHERE room_id IN (SELECT room_id FROM validate_room_mapping WHERE batch_name LIKE "{}%" )'.format(battle_name)
        self.cursor.execute(game_sql)
        result = self.cursor.fetchall()
        for row in result:
            game_id, public_card, action_history, battle_time, room_id = row[:5]
            history[game_id] = dict(
                public_card=public_card, 
                action_history=self.transpose(json.loads(action_history)),
                battle_time=battle_time.strftime('%Y-%m-%d %H:%M:%S' ),
                players={}
            )
        
        game_sql = 'SELECT game_id, position, win_money, private_card, name FROM player WHERE room_id IN (SELECT room_id FROM validate_room_mapping WHERE batch_name LIKE "{}%" )'.format(battle_name)
        self.cursor.execute(game_sql)
        result = self.cursor.fetchall()
        for row in result:
            game_id, position, win_money, private_card, name = row[:]
            history[game_id]["players"][int(position)] = dict(
                win_money=float(win_money),
                private_card=private_card,
                name=name                
            )
        if save_file:
            with open("{}_history.json".format(battle_name), "w") as f:
                json.dump(history, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
