import redis
import json
import uuid
from logs import logger
from config import cfg


class Redis():
    def __init__(self):
        self.r = redis.Redis(host=cfg["redis"]["host"], port=cfg["redis"]["port"], decode_responses=True, password=cfg["redis"]["password"])

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
