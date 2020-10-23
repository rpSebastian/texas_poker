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
    time.sleep(10)

login()

# battle(6, 5000, ["TestAI", "YuanWeilin"], "TestAI vs nudt")

battle(2, 5000, ["RandomGambler","LooseAggressive","LoosePassive","TightPassive","TightAggressive","Hitsz"], "Hit_6p_test")

