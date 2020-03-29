import socket
import selectors

num = 1
sel = selectors.DefaultSelector()


def accept(sock):
    client, addr = sock.accept()
    sel.register(client, selectors.EVENT_READ, read)


def read(sock):
    data = sock.recv(100).decode()
    if data:
        print(data)
        global num
        num += 1
        sock.send(data.encode())
        print(num)
    else:
        sel.unregister(sock)
        sock.close()


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('127.0.0.1', 12357))
server.listen(20)
sel.register(server, selectors.EVENT_READ, accept)
while True:
    events = sel.select()
    for key, _ in events:
        callback = key.data
        callback(key.fileobj)
