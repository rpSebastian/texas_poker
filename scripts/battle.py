import json
import requests
import time

headers = {
    "Content-Type": "application/json;charset=UTF-8",
    "Cookie": "0JvO_2132_saltkey=wZEJz1e1; 0JvO_2132_lastvisit=1602752836; 0JvO_2132_ulastactivity=c9e0AZ3QtnTjfvxeaIVx1NGEvRo7OLrjSIM30f26lQfWPWchDIoc; 0JvO_2132_lastcheckfeed=14%7C1602756436; 0JvO_2132_nofavfid=1"
    
}

def login():
    url = "http://holdem.ia.ac.cn:9001/login"

    data = {
        "email": "cxxuhang@126.com",
        "password": "zxc123456"
    }

    r_json = requests.post(url=url, data=json.dumps(data), headers=headers)
    token = r_json.json()["result"]
    headers["token"] = token

def battle(parallel, game_number, botList, battleName):
    for i in range(parallel):
        url = "http://holdem.ia.ac.cn:9002/BatchValidate/submitValidate"
        data = {
            "AISum": len(botList),
            "batchName": battleName + "_" + str(i),
            "battleCount": str(game_number),
            "botList": ','.join(botList),
            "roomCount": str(len(botList)),
            "validateType": "raw"
        }
        r_json = requests.post(url=url, data=json.dumps(data), headers=headers)
        print(r_json.json())

login()

battle(6, 5000, ["OpenStackTwo", "YuanWeilin"], "NewStack_argmax vs nudt")

# battle(14, 5000, ["TightAggressive","TightPassive","RandomGambler","ScaredLimper","CandidStatistician","Hitsz"], "Hit_6p_test2")

# battle(4, 1000, ["RuleAgent6p", "RuleAgent6p", "RuleAgent6p", "Hitsz", "Hitsz", "Hitsz"], "Rule_vs_hitsz")


battle(8, 2000, ["CandidStatistician","TightPassive","QianTao","RuleAgent6p","Hitsz","HitszTwo"], "Test6p")