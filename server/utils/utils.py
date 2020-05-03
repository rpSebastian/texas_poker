import json
import struct
from err import MyError

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
