import numpy as np
import matplotlib.pyplot as plt
import pymysql
from collections import defaultdict
from scipy import stats 

def main():
    import sys
    mysql = Mysql()
    # for agent in ['TestCall', 'TestRandomAll', 'TestHalfCR']:
    #     for lbr in ['lbr-fc-1-4', 'lbr-fc-3-4', 'lbr-fcpa-1-4', 'lbr-fcpa-3-4']:
    #         mysql.query_money(lbr, agent)
    for data_count in [1, 2, 3, 4]:
        for version in [1, 2]:
            agent = 'x.h.v' + str(data_count) + 'm.' + str(version)
            mysql.query_money(agent, 'slumbot')
    for data_count in [1, 2, 3, 4]:
        for version in [1]:
            agent = 'x.h.v' + str(data_count) + 'm.' + str(version)
            mysql.query_money(agent, 'lbr-fc-1-4')
    mysql.query_money('x.h.v1m.1', 'RuleAgent0')
    # mysql.query_record('x.h.v4m.1', 'RuleAgent0')
    # mysql.count_all('lbr-fcpa-3-4', 'random2')


    # mysql.query_money('lbr-fc-1-4', 'TestRandom')
    # mysql.query_all()
    # mysql.count_all()
    # mysql.query_record('x.h.v2.4')
    mysql.end()

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
 
    def query_money(self, name1, name2, show=False):
        sql = "SELECT win_money FROM player where player.name like %s and player.game_id in  (SELECT game_id FROM player where player.name like %s)"
        self.cursor.execute(sql, (name1, name2)) 
        win_moneys = []
        for row in self.cursor.fetchall():
            win_moneys.append(row[0])
        n = len(win_moneys)
        win_moneys = np.array(win_moneys)
        mean, sigma = np.mean(win_moneys), np.std(win_moneys)
        conf_int = stats.norm.interval(0.95, loc=mean, scale=sigma / np.sqrt(len(win_moneys)))
        dis = conf_int[1] - mean
        # print('{}, {} match {} hands, win {:.2f} bb/100g ± {:.2f} bb/100g'.format(name1, name2, n, np.mean(win_moneys) , dis))
        print('{:20} \t {:20} \t {:.2f} ± {:.2f} \t {}'.format(name1, name2, np.mean(win_moneys) , dis , n))
        mbb = self.calc_mbb(win_moneys)
        if show:
            plt.hlines(0, 0, n,color="red")
            # plt.plot(mbb)
            plt.plot(win_moneys)
            plt.show()
        # plt.hlines(0, 0, n,color="red")
        # plt.plot(win_moneys)
        # plt.show()


    def query_record(self, name1, name2, money = None):
        sql1 = "SELECT game_id FROM player where player.name = %s and player.game_id in  (SELECT game_id FROM player where player.name = %s)"
        sql2 = "SELECT game_id FROM player where player.win_money = %s and player.name = %s and player.game_id in  (SELECT game_id FROM player where player.name = %s)"
        if money is None:
            self.cursor.execute(sql1, (name1, name2))
        else:
            self.cursor.execute(sql2, (money, name1, name2))
        game_ids = []
        for row in self.cursor.fetchall():
            game_ids.append(row[0])
        for game_id in game_ids:
            sql = "SELECT public_card, action_history FROM game where game.game_id = %s"
            self.cursor.execute(sql, game_id)
            for row in self.cursor.fetchall():
                public_card, action_history = row
            sql = "SELECT position, private_card, win_money FROM player where player.name = %s and player.game_id = %s"
            self.cursor.execute(sql, (name1, game_id))
            for row in self.cursor.fetchall():
                position, private_card, win_money = row
            sql = "SELECT private_card FROM player where player.name = %s and player.game_id = %s"
            self.cursor.execute(sql, (name2, game_id))
            for row in self.cursor.fetchall():
                opp_card = row[0]
            print(position, public_card, private_card, opp_card, int(win_money), action_history)
            print()

    def calc_mbb(self, array):
        cnt = 0
        sums = []
        for i, a in enumerate(array):
            cnt += a
            sums.append(cnt / (i+1) )
        return np.array(sums)

    def end(self):
        self.cursor.close()
        self.content.close()

    def count_all(self, name1, name2):
        win_moneys = []
        sql = "SELECT win_money FROM player where player.name = %s and player.game_id in  (SELECT game_id FROM player where player.name = %s)"
        self.cursor.execute(sql, (name1, name2)) 
        for row in self.cursor.fetchall():
            win_moneys.append(row[0])
        a = defaultdict(int)
        for i in win_moneys:
            a[str(int(i))] += 1
        result = []
        for key, value in a.items():
            result.append((key, value))
        result = sorted(result, key=lambda x: abs(int(x[0])), reverse=True)
        for key, value in result:
            if value > 10:
                print(key, ':', value)

if __name__ == '__main__':
    main()
