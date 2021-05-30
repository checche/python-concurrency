"""
スレッドの公平性担保のために、
処理の途中に別スレッドの処理の割り込みが発生する事がある。
スレッドセーフにするためにはLockクラスを用いる
"""

# %%
from threading import Lock, Thread


# %%
class LockingCounter:
    def __init__(self) -> None:
        self.lock = Lock()
        self.count = 0

    def increment(self, offset):
        with self.lock:  # 処理の相互排他ロックを行うコンテキスト
            self.count += offset


def worker(sensor_index, how_many, counter):
    for _ in range(how_many):
        counter.increment(1)


# %%
how_many = 10 ** 5
counter = LockingCounter()
threads = []
for i in range(5):
    thread = Thread(target=worker, args=(i, how_many, counter))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

expected = how_many * 5
found = counter.count
print(f"Counter should be {expected}, got {found}")

# %%
