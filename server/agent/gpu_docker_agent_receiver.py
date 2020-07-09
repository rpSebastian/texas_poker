import time
import pika
import json
import GPUtil
import redis
import subprocess
import collections
import subprocess

credentials = pika.PlainCredentials("root", "root")
connection = pika.BlockingConnection(
	pika.ConnectionParameters(
		host="172.18.40.65",
		credentials=credentials,
		heartbeat=0
	))
channel = connection.channel()

channel.queue_declare(queue='agent_error_queue')

supported_agent = ["OpenStack"]
GpuNeeded = {
	"OpenStack": 4000, 
}

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
				if time.time() - use_time < 90:
					initialing_amount += amount
			if gpu.memoryFree - initialing_amount - 1000 > gpu_needed:
				gpu_available = True
				break
		if gpu_available:
			self.last_use[gpu.id].append([time.time(), gpu_needed])
			while time.time() - self.last_use[gpu.id][0][0] > 90:
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
				'docker run -d --rm --gpus "device={}" -v /home/xuhang/code/LuaStack:/root/LuaStack cxxuhang/luastack:lua-python-base bash -c "cd /root/LuaStack && bash scripts/activate_agent.sh {} {} {} {}"'.format(
					gpu_id, room_id, room_number, bot_name + bot_name_suffix, game_number)
			)
			print(command)
		subprocess.call(command, shell=True)
	else:
		data["no_gpu"] += 1
		if data["no_gpu"] >= 10:
			data["error"] = "no_gpu"
			channel.basic_publish(exchange='', routing_key='agent_error_queue', body=json.dumps(data))
		else:
			channel.basic_publish(exchange='', routing_key=bot_name, body=json.dumps(data))
	
	ch.basic_ack(method.delivery_tag)

for agent in supported_agent:
	channel.basic_consume(queue=agent, on_message_callback=callback)
channel.start_consuming()
