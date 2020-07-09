import time
import pika
import json
import subprocess
import collections
import simple_agent
import subprocess
import redis

supported_agent = ["CallAI"]

credentials = pika.PlainCredentials("root", "root")
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host="172.18.40.65",
        credentials=credentials,
        heartbeat=0
    ))
channel = connection.channel()

r = redis.Redis(host="172.18.40.65", port="6379", decode_responses=True, password="root")

for agent in supported_agent:
    channel.queue_declare(queue=agent)
    if r.exists("supported_agent"):
        result = json.loads(r.get("supported_agent"))
    else:
        result = []
    if agent not in result:
        result.append(agent)
    r.set("supported_agent", json.dumps(result))

print(result)


def callback(ch, method, properties, body):
    data = json.loads(body)
    print(data)
    room_id = data["room_id"]
    room_number = data["room_number"]
    game_number = data["game_number"]
    bot_name = data["bot_name"]
    bot_name_suffix = data["bot_name_suffix"]
    
    if bot_name == "CallAI":
        command = (
            'docker run --rm registry.cn-hangzhou.aliyuncs.com/xuhang/agent:demo bash -c "cd /root/project && python demo.py {} {} {} {}"'.format(
            room_id, room_number, bot_name + bot_name_suffix, game_number)
        )
        print(command)
        subprocess.call(command, shell=True)
    
    ch.basic_ack(method.delivery_tag)


for agent in supported_agent:
    channel.basic_consume(queue=agent, on_message_callback=callback)
channel.start_consuming()

