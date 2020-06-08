import redis
import json
import uuid

r = redis.Redis(host='localhost', port=6379, decode_responses=True, password="root")

info = {"x": 1}
pid = str(uuid.uuid4())
r.set(pid, json.dumps(info))
result = r.get(pid)
print(json.loads(result))
