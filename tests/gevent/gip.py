import gevent
import multiprocessing

def writelet(c):
    c.send(0)

def readchild(c):
    gevent.sleep(0)
    assert c.recv() == 0
    assert c.recv() == 0

if __name__ == "__main__":
    c1, c2 = multiprocessing.Pipe()
    g = gevent.spawn(writelet, c1)
    p = multiprocessing.Process(target=readchild, args=(c2,))
    p.start()
    g.join()
    p.join()