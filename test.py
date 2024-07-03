import threading
from datetime import datetime
import time

bpm = 100

def more_than_2_threads():
    return len(threading.enumerate()) > 2

def tick():
    t0 = datetime.now()
    num_of_ticks = 0
    time_per_beat = 60 / bpm

    while True:
        if more_than_2_threads():
            break
   
        start = time.time()
           
        num_of_ticks += 1
        if more_than_2_threads():
            break
        print('tick')
        end = time.time()
        delay = end - start
            # print(delay)
        if delay < time_per_beat:
            time.sleep(time_per_beat - delay)  # click_accented_long.waw is 0.03s longer


def tick_threaded(enabled):
    num_of_ticks = 0
    thread = threading.Thread(target=tick, args=(enabled,))
    thread.start()
    num_of_ticks += 1
    if more_than_2_threads():
        threading.enumerate()[1].join()
        
    print(threading.enumerate())

def exit_tick_threaded():
    if len(threading.enumerate()) > 1:
        print(threading.get_ident())
        threading.enumerate()[1].join()

tick()