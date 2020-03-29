import time
import asyncio
from threading import Thread

def start_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

async def get_message():
    # raise Exception()
    return 'Hello'

async def do(x):
    print('do', x)
    try:
        result = await get_message()
    except Exception:
        print('error')
    print(result)
    print('finish', x)
    return 'Done'

def callback(future):
    print('Callback: ', future.result())


start = time.time()
# loop = asyncio.get_event_loop()
loop = asyncio.new_event_loop()
t = Thread(target=start_loop, args=(loop, ))
t.start()

coroutine = do(2)
task = asyncio.ensure_future(coroutine)
task.add_done_callback(callback)
asyncio.run_coroutine_threadsafe(task, loop)
# loop.run_until_complete(asyncio.wait([coroutine, coroutine2, coroutine3]))
print('TIME',  time.time() - start)
