import struct
import json
from twisted.internet import protocol
from logs import logger


class JsonReceiver(protocol.Protocol):

    _buffer = b''

    def dataReceived(self, data):
        try:
            self._buffer += data
            while len(self._buffer) >= 4:
                length = struct.unpack('i', self._buffer[:4])[0]
                if len(self._buffer) < length + 4:
                    break
                message = json.loads(self._buffer[4:length + 4].decode())
                self._buffer = self._buffer[length + 4:]
                self.jsonReceived(message)
        except Exception as e:
            logger.exception(e)
            self.transport.loseConnection()

    def jsonReceived(self, message):
        raise NotImplementedError

    def sendJson(self, message):
        message = json.dumps(message).encode()
        data = struct.pack('i', len(message)) + message
        return self.transport.write(data)
