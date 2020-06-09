import json
import struct
from logs import logger
from err import MyError
import subprocess
myip = subprocess.check_output(["hostname", "-I"]).decode().split(" ")[0]


def sendJson(request, jsonData):
    try:
        data = json.dumps(jsonData).encode()
        request.send(struct.pack('i', len(data)) + data)
    except (BrokenPipeError, ConnectionResetError):
        raise MyError()


def recvJson(request):
    try:
        data = request.recv(4)
        if data == b"":
            raise MyError()
        length = struct.unpack('i', data)[0]
        data = request.recv(length).decode()
        while len(data) != length:
            data = data + request.recv(length - len(data)).decode()
        if data == "":
            raise MyError()
        data = json.loads(data)
        return data
    except (BrokenPipeError, ConnectionResetError):
        raise MyError()


def catch_exception(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.exception(e)
    return wrapper
