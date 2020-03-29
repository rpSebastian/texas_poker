import json
import struct


class DisconnectException(Exception):
    def __init__(self, text):
        self.text = text


def sendJson(request, jsonData):
    data = json.dumps(jsonData).encode()

    request.send(struct.pack('i', len(data)))
    request.sendall(data)


def recvJson(request):
    data = request.recv(4)
    if data == b"":
        raise DisconnectException('disconnect')
    length = struct.unpack('i', data)[0]
    data = request.recv(length).decode()
    while len(data) != length:
        data = data + request.recv(length - len(data)).decode()
    if data == "":
        raise DisconnectException('disconnect')
    data = json.loads(data)
    return data
