import json
import struct
from err import DisconnectException


def sendJson(request, jsonData):
    try:
        data = json.dumps(jsonData).encode()
        request.send(struct.pack('i', len(data)))
        request.sendall(data)
    except (BrokenPipeError, ConnectionResetError):
        raise DisconnectException()

def recvJson(request):
    try:
        data = request.recv(4)
        if data == b"":
            raise DisconnectException()
        length = struct.unpack('i', data)[0]
        data = request.recv(length).decode()
        while len(data) != length:
            data = data + request.recv(length - len(data)).decode()
        if data == "":
            raise DisconnectException()
        data = json.loads(data)
        return data
    except (BrokenPipeError, ConnectionResetError):
        raise DisconnectException()
