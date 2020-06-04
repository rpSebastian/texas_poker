import redis
import json
import uuid
from logs import logger


class Redis():
    def __init__(self):
        self.r = redis.Redis(host='localhost', port=6379, decode_responses=True, password="root")

    def save_message(self, message):
        pid = str(uuid.uuid4())
        self.r.set(pid, json.dumps(message), ex=120)
        return pid

    def load_message(self, pid):
        try:
            message = json.loads(self.r.get(pid))
            return message
        except Exception:
            logger.error('Redis Key Error')
