from .mysql import Mysql
import pandas as pd
import json
import numpy as np
import pandas as pd
import subprocess
from collections import defaultdict
from tqdm import tqdm

class Statistician():
    def __init__(self):
        self.db = Mysql()

    def query_record_by_room_name(self, room_name, game_limit=None):
        bot_names = self._query_bot_names_by_room_name(room_name)
        
        # 查询game表，获取对战公共记录
        record = {}
        sql = ('SELECT game_id, public_card, action_history, time FROM game '
               'WHERE room_id IN (select room_id from validate_room_mapping '
               'where batch_name like "{}%")'.format(room_name))
        result = self.db.query(sql)

        for row in tqdm(result):
            game_id, public_card, action_history, battle_time = row[:5]
            record[game_id] = dict(
                public_card=public_card, 
                action_history=self._transpose(json.loads(action_history)),
                battle_time=battle_time.strftime('%Y-%m-%d %H:%M:%S' ),
                players={}
            )
            # 达到限制条数, 退出循环
            if game_limit and len(record) == game_limit:
                break
        
        # 查询player表，获取每个AI的具体信息，插入对应公共记录中
        sql = ('SELECT game_id, position, win_money, private_card, name FROM player '
               'WHERE room_id IN (select room_id from validate_room_mapping where batch_name '
               'like "{}%")'.format(room_name))
        result = self.db.query(sql)
        for row in tqdm(result):
            game_id, position, win_money, private_card, name = row[:]
            # game表中没有, player表中有
            if not game_id in record:
                continue
            record[game_id]["players"][int(position)] = dict(
                win_money=float(win_money),
                private_card=private_card,
                name=name      
            )

        # 过滤不匹配数据, 不合法数据, 限制数据条数
        actual_record = {}
        for game_id, game in record.items():
            # 过滤player表中有, game表中没有
            if len(game["players"]) == 0:
                continue

            # 过滤非房间对战 AI 数据
            name_err = False
            for position, player in game["players"].items():
                if not player["name"] in bot_names:
                    name_err = True
                    break
            if name_err:
                continue

            actual_record[game_id] = game
        
            # 限制数据条数
            if game_limit and len(actual_record) == game_limit:
                break
            
        # 保存对战数据
        with open("../data/record/{}_history.json".format(room_name), "w") as f:
            json.dump(actual_record, f, indent=4, ensure_ascii=False)

    def query_result_by_room_name(self, room_name, reduce_variance=True):

        # 读取对战数据
        with open("../data/record/{}_history.json".format(room_name), "r") as f:
            record = json.load(f)
        
        # 获取 AI 名字
        bot_names = self._query_bot_names_by_room_name(room_name)

        # 模拟 allin 方差缩减目前只适用于两人
        if reduce_variance and len(bot_names) != 2:
            raise ValueError("模拟 allin 方差缩减目前只适用于两人")

        # 获取 AI 对战收益筹码
        bot_win = {name: [] for name in bot_names}
        for game_id, game in tqdm(record.items()):
            action_history = game["action_history"]
            round_num = len(action_history.split("/"))
            public_card = game["public_card"]
            for position, player in game["players"].items():
                name, win = player["name"], player["win_money"]
                if reduce_variance and abs(win) == 20000 and round_num != 4:
                    private_card = player["private_card"]
                    opp_card = game["players"][str(1 - int(position))]["private_card"]
                    board_num = [0, 3, 4, 5][round_num - 1]
                    board = public_card[:board_num * 2]
                    win = 20000 * self._calc_relative_win_prop(private_card, opp_card, board)
                bot_win[name].append(win)

        # 统计数据
        table = pd.DataFrame(columns=['AI名字', '总局数', '累积收益筹码', '场均收益筹码', '0.95置信区间'])
        for bot in bot_names:
            win = bot_win[bot]
            num, total, mean, std = len(win), np.sum(win), np.mean(win), np.std(win)
            interval = 1.96 * std / np.sqrt(num)
            table.loc[table.shape[0]] = [bot, num, total, mean, interval]
        
        # 保存excel
        if reduce_variance:
            name = "../data/record/{}_stat_reduce.xlsx".format(room_name)
        else:
            name = "../data/record/{}_stat.xlsx".format(room_name)
        writer = pd.ExcelWriter(name)  
        table.to_excel(writer, float_format='%.4f', index=None)
        writer.save()
        
    def _calc_relative_win_prop(self, hand, opp_hand, board = None):
        if board is None or board == "":
            status, res = subprocess.getstatusoutput("./pokerstove/build/bin/ps-eval {} {}".format(hand, opp_hand))
        else:
            status, res = subprocess.getstatusoutput("./pokerstove/build/bin/ps-eval {} {} --board {}".format(hand, opp_hand, board))
        line1, line2 = res.split("\n")
        p1 = float(line1.split(" ")[4])
        p2 = float(line2.split(" ")[4])
        return (p1 - p2) / 100
    
    def _query_bot_names_by_room_name(self, room_name):
        # 获取 AI 名字
        sql = 'select bot_list from batch_ai_validate where batch_name like "{}%"'.format(room_name)
        result = self.db.query(sql)
        bot_names = result[0][0].split(',')
        return bot_names

    def _transpose(self, action_history):
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