import context
from room import RoomManager
import signal
from config import cfg
signal.signal(signal.SIGCHLD, signal.SIG_IGN)

for i in range(cfg["room_manager"]["num"]):
    p = RoomManager(i)
    p.start()
