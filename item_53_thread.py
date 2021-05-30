"""
GILがあるため、Pythonではマルチスレッドを使ってもCPUのマルチコアを利用できない。

Pythonがスレッドをサポートしている理由
1. 複数のことをしているのがわかりやすくなる
2. ブロッキングI/Oを扱うときに使うとよい
Pythonはシステムコール前にGILの開放を、システムコール後にGILの獲得を行う。
システムコール中にGILが行われないためシステムコールは並列に実行できる。
"""
# %%
import select
import socket
import time
from threading import Thread
from typing import List


# %%
def slow_systemcall():
    select.select([socket.socket()], [], [], 1)


def compute_helicopter_location(index):
    ...


# %%
start = time.time()

for _ in range(5):
    slow_systemcall()

end = time.time()
delta = end - start
print(f"Took {delta:.3f} seconds")

# %%

start = time.time()

threads: List[Thread] = []

for i in range(5):
    thread = Thread(target=slow_systemcall)  # 並列実行を行う
    thread.start()
    threads.append(thread)

for i in range(5):
    compute_helicopter_location(i)

for thread in threads:
    thread.join()  # スレッドの実行を待つ

end = time.time()
delta = end - start
print(f"Took {delta:.3f} seconds")


# %%
