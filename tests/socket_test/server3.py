import socket
import selectors
import asyncio
from threading import Thread


def start_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


sel = selectors.DefaultSelector()
loop = asyncio.new_event_loop()
t = Thread(target=start_loop, args=(loop, ))
t.setDaemon(True)
t.start()


async def work(sock):
    data = sock.recv(100).decode()
    sock.send(data.encode())
    print(data)
    data = sock.recv(100).decode()
    sock.send(data.encode())
    print(data)


def accept(sock):
    client, addr = sock.accept()
    coroutine = work(client)
    # task = asyncio.ensure_future(coroutine)
    # task.add_done_callback(callback)
    asyncio.run_coroutine_threadsafe(coroutine, loop)


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('127.0.0.1', 12359))
server.listen(20)
sel.register(server, selectors.EVENT_READ, accept)
while True:
    events = sel.select()
    for key, _ in events:
        callback = key.data
        callback(key.fileobj)
