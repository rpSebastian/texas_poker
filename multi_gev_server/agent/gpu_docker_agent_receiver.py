import os
import time
import pika
import pymysql
import json
import GPUtil
import redis
import subprocess
import collections
import subprocess

docker_version = int(os.popen("docker version | grep Version | awk '{print $2}'  | head -1").read().strip().split(".")[0])
docker_gpu_command = (lambda x: ' --gpus "device={}" '.format(x)) if docker_version==19 else (lambda x: " --runtime=nvidia -e NVIDIA_VISIBLE_DEVICES={} ".format(x))

if docker_version == 19:
	supported_agent = ["OpenStack", "YuanWeilin"]
else:
	supported_agent = ["OpenStack", "TestAI", "Hitsz", "HitszTwo", "OpenStackTwo", "YuanWeilin"]

GpuNeeded = {
	"OpenStack": 5000,
	"YuanWeilin": 5000,
	"TestAI": 10000,
	"Hitsz": 5000,
	"HitszTwo": 5000,
	"OpenStackTwo": 5000,
}

class GpuManager():
	def __init__(self):
		self.last_use = collections.defaultdict(list)
	
	def get_gpu_id(self, bot_name):
		GPUs = GPUtil.getGPUs()
		gpu_available = False
		gpu_needed = GpuNeeded[bot_name]
		for gpu in GPUs:
			initialing_amount = 0
			for use_time, amount in reversed(self.last_use[gpu.id]):
				if time.time() - use_time < 600:
					initialing_amount += amount
			if gpu.memoryFree - initialing_amount - 1000 > gpu_needed:
				gpu_available = True
				break
		if gpu_available:
			self.last_use[gpu.id].append([time.time(), gpu_needed])
			while time.time() - self.last_use[gpu.id][0][0] > 600:
				self.last_use[gpu.id].pop(0)
			return True, gpu.id
		else:
			return False, None

gpu_manager = GpuManager()


def callback(ch, method, properties, body):
	data = json.loads(body)
	print(data)
	room_id = data["room_id"]
	room_number = data["room_number"]
	game_number = data["game_number"]
	bot_name = data["bot_name"]
	bot_name_suffix = data["bot_name_suffix"]
	
	gpu_available, gpu_id = gpu_manager.get_gpu_id(bot_name)
	if gpu_available:
		if bot_name == "OpenStack":
			command = (
				'docker run -d {} hub.kce.ksyun.com/cxxuhang/openstack:v0.1 bash -c "cd /root/LuaStack && bash scripts/activate_agent.sh {} {} {} {}"'.format(
					docker_gpu_command(gpu_id), room_id, room_number, bot_name + bot_name_suffix, game_number)
			)
			print(command)
		if bot_name == "OpenStackTwo":
			command = (
				'docker run -d {} hub.kce.ksyun.com/cxxuhang/openstack:v4.1 bash -c "cd /root/OpenStack && bash scripts/activate_agent.sh {} {} {} {}"'.format(
					docker_gpu_command(gpu_id), room_id, room_number, bot_name + bot_name_suffix, game_number)
			)
			print(command)
		if bot_name == "YuanWeilin":
			command = (
				'docker run -d {} registry.cn-beijing.aliyuncs.com/poker_ws/deepcard:v13 bash -c "source /root/torch/install/bin/torch-activate;cd /code/ReadyCompile/Compiled;th Player/deepcards.lua {} {} {} {}"'.format(
					docker_gpu_command(gpu_id), room_id, room_number, bot_name + bot_name_suffix, game_number)
			)
			print(command)
		if bot_name == "TestAI":
			command = (
				'docker run -d {} hub.kce.ksyun.com/cxxuhang/openstack:v3.2 bash -c "cd /root/LuaStack && bash scripts/activate_agent.sh {} {} {} {}"'.format(
					docker_gpu_command(gpu_id), room_id, room_number, bot_name + bot_name_suffix, game_number)
			)
			print(command)
		if bot_name == "Hitsz":
			command = (
            'docker run -d {} hub.kce.ksyun.com/cxxuhang/openstack:6p_v1.6 bash -c "cd /root/openstackv1/Source && th Player/deepstack_server_agent_6p.lua {} {} {} {}"'.format(
            docker_gpu_command(gpu_id), room_id, room_number, bot_name + bot_name_suffix, game_number)
        )
			print(command)
		if bot_name == "HitszTwo":
			command = (
            'docker run -d {} hub.kce.ksyun.com/cxxuhang/openstack:6p_v2.1 bash -c "cd /root/openstackv1/Source && th Player/deepstack_server_agent_6p.lua {} {} {} {}"'.format(
            docker_gpu_command(gpu_id), room_id, room_number, bot_name + bot_name_suffix, game_number)
        )
			print(command)

		subprocess.call(command, shell=True)
	else:
		data["no_gpu"] += 1
		if data["no_gpu"] >= 10:
			data["error"] = "no_gpu"
			ch.basic_publish(exchange='', routing_key='agent_error_queue', body=json.dumps(data))
		else:
			ch.basic_publish(exchange='', routing_key=bot_name, body=json.dumps(data))
	
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
