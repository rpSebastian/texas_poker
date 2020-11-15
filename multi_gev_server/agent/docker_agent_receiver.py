import os
import time
import pika
import pymysql
import json
import subprocess
import collections
import subprocess


supported_agent = ["xxx", "YangJun", "LiShuokai", "QianTao", "CFRAgent"]

def callback(ch, method, properties, body):
    data = json.loads(body)
    print(data)
    room_id = data["room_id"]
    room_number = data["room_number"]
    game_number = data["game_number"]
    bot_name = data["bot_name"]
    bot_name_suffix = data["bot_name_suffix"]
    
    if bot_name == "xxx":
        command = (
            'docker run -d --rm registry.cn-hangzhou.aliyuncs.com/xuhang/agent:demo bash -c "cd /root/project && python demo.py {} {} {} {}"'.format(
            room_id, room_number, bot_name + bot_name_suffix, game_number)
        )
        print(command)
        subprocess.call(command, shell=True)

    if bot_name == "YangJun" or bot_name == "CFRAgent":
        command = (
            'docker run -d registry.cn-beijing.aliyuncs.com/liuqh/texas2:v1.2 bash -c "cd /root/poker && export PATH=/root/miniconda3/bin:$PATH && python run_this.py {} {} {} {}"'.format(
            room_id, room_number, bot_name + bot_name_suffix, game_number)
        )
        print(command)
        subprocess.call(command, shell=True)

    if bot_name == "LiShuokai":
        command = (
            'docker run -d registry.cn-beijing.aliyuncs.com/xuehongyan/ict_agent:v0.1.2 bash -c "cd /root/project && python py_player_new.py {} {} {} {}"'.format(
            room_id, room_number, bot_name + bot_name_suffix, game_number)
        )
        print(command)
        subprocess.call(command, shell=True)

    if bot_name == "QianTao":
        command = (
            'docker run -d registry.cn-shenzhen.aliyuncs.com/hitszcs/hitsz6p:v1.4 bash -c "cd /root/project && python agent_cas.py {} {} {} {}"'.format(
            room_id, room_number, bot_name + bot_name_suffix, game_number)
        )
        print(command)
        subprocess.call(command, shell=True)
    
    ch.basic_ack(method.delivery_tag)


def declare_queue():
    credentials = pika.PlainCredentials("root", "root")
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host="172.18.40.65",
            credentials=credentials,
            heartbeat=0
        ))
    channel = connection.channel()
    for agent in supported_agent:
        channel.queue_declare(queue=agent)
    for agent in supported_agent:
        channel.basic_consume(queue=agent, on_message_callback=callback)
    channel.start_consuming()

def update_database():
    connect = pymysql.Connect(
        host="172.18.40.65",  # mysql的主机ip
        port=3306,  # 端口
        user="root",  # 用户名
        passwd="root",  # 数据库密码
        db="poker",  # 数据库名
        charset='utf8',  # 字符集
    )
    cursor = connect.cursor()
    select_sql = 'select name from agent'
    cursor.execute(select_sql)
    cursor.connection.commit()
    results = cursor.fetchall()
    agents = [result[0] for result in results]
    update_sql = "insert into agent(name) values (%s)"
    for agent in supported_agent:
        if agent not in agents:
            cursor.execute(update_sql, agent)
            cursor.connection.commit()


if __name__ == "__main__":
    update_database()
    declare_queue()
