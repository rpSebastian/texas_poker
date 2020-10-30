import json
import struct
from utils.logs import logger

def sendJson(request, jsonData):
    try:
        data = json.dumps(jsonData).encode()
        request.send(struct.pack('i', len(data)) + data)
        return True
    except (BrokenPipeError, ConnectionResetError):
        return False


def recvJson(request):
    try:
        data = request.recv(4)
        if data == b"":
            return None
        length = struct.unpack('i', data)[0]
        data = request.recv(length).decode()
        while len(data) != length:
            data = data + request.recv(length - len(data)).decode()
        if data == b"":
            return None
        data = json.loads(data)
        return data
    except (BrokenPipeError, ConnectionResetError):
        return None


def catch_exception(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.exception(e)
    return wrapper

def run_forever(func):
    def wrapper(*args, **kwargs):
        while True:
            func(*args, **kwargs)
    return wrapper


if __name__ == "__main__":

    def func(s):
        import time
        time.sleep(s)
        print("ok")

    with time_limit(3):
        func(2)