from game_stat.lookup import Statistician
import multiprocessing
import pandas as pd 
import numpy as np
import json

def run(name):
    Statistician().query_record_by_room_name(name)
    Statistician().query_result_by_room_name(name, reduce_variance=False)
    # Statistician().query_result_by_room_name(name, reduce_variance=True)


def get_table():
    names = ["NUDT", "IA", "THU", "ICT"]
    ai_names = ["YuanWeilin", "OpenStackTwo", "YangJun", "LiShuokai"]
    table = pd.DataFrame(columns=["NUDT", "IA", "THU", "ICT"])
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            n1 = names[i]
            n2 = names[j]
            # table = pd.read_excel('../data/record/TEST_{}_{}_stat_reduce.xlsx'.format(n1, n2)) 
            # print(table)
            with open("../data/record/TEST_{}_{}_history.json".format(n1, n2), "r") as f:
                record = json.load(f)
            print(len(record))


# names = ["TEST_NUDT_THU", "TEST_IA_ICT", "TEST_NUDT_ICT", "TEST_NUDT_IA", "TEST_IA_THU", "TEST"]    
# limits = [100000, 100000, 100000, 200000, 100000, 100000]

# process = []
# for name, limit in zip(names, limits):
#     p = multiprocessing.Process(target=run, args=(name, limit))
#     process.append(p)
#     p.start()
# for p in process:
#     p.join()

run("2020_11_23_Test_6p")