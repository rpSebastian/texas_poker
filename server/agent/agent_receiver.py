import time
import pymysql
import pika
import redis
import json
import subprocess
import collections
import simple_agent


supported_agent = ["CallAgent", "AllinAgent", "RandomAgent"]


def callback(ch, method, properties, body):
    data = json.loads(body)
    room_id = data["room_id"]
    room_number = data["room_number"]
    game_number = data["game_number"]
    bot_name = data["bot_name"]
    bot_name_suffix = data["bot_name_suffix"]
    server = data["server"]
    port = data["port"]
    if bot_name == "CallAgent":
        simple_agent.CallAgent(room_id, room_number, bot_name + bot_name_suffix, game_number, server, port).start()
    if bot_name == "AllinAgent":
        simple_agent.AllinAgent(room_id, room_number, bot_name + bot_name_suffix, game_number, server, port).start()
    if bot_name == "RandomAgent":
        simple_agent.RandomAgent(room_id, room_number, bot_name + bot_name_suffix, game_number, server, port).start()
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
