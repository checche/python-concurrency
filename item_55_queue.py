"""
Producer/Consumerをつかった関数パイプラインは並行作業を行う際に役立つ
Queueを使うと良い感じ

SENTINEL: キューに今後の入力が無いことを示す要素
Queue.get(): put()があるまで自動的に処理を待ってくれる
Queue.join(): task_done()が呼び出されるまで処理を待ってくれる
"""
# %%
import select
import socket
import time
from queue import Queue
from threading import Thread


# %%
def download(item):
    select.select([socket.socket()], [], [], 0.3)
    return item


def resize(item):
    select.select([socket.socket()], [], [], 0.4)
    return item


def upload(item):
    select.select([socket.socket()], [], [], 0.5)
    return item


# %%
class StoppableWorker(Thread):
    def __init__(self, func, in_queue, out_queue):
        super().__init__()
        self.func = func
        self.in_queue = in_queue
        self.out_queue = out_queue

    def run(self):
        for item in self.in_queue:
            result = self.func(item)
            self.out_queue.put(result)


# %%
class ClosableQueue(Queue):
    SENTINEL = object()

    def close(self):
        self.put(self.SENTINEL)

    def __iter__(self):
        """キューの次の要素を取り出す。SENTINELが出たら反復処理を停止する

        Yields:
            [type]: キューに格納されたデータ
        """
        while True:
            item = self.get()
            try:
                if item is self.SENTINEL:
                    return
                yield item
            finally:
                self.task_done()


# %%
def start_threads(count, *args):
    threads = [StoppableWorker(*args) for _ in range(count)]
    for thread in threads:
        thread.start()
    return threads


def stop_threads(closable_queue, threads):
    # 消費者スレッドごとに各入力キューを閉じることで、
    # 作業者スレッドの終了を確実にする
    for _ in threads:
        closable_queue.close()

    # 要素を取り出し、task_done()がよばれるまで待機する
    closable_queue.join()

    for thread in threads:
        thread.join()


# %%
download_queue = ClosableQueue()
resize_queue = ClosableQueue()
upload_queue = ClosableQueue()
done_queue = ClosableQueue()
start = time.time()
download_threads = start_threads(8, download, download_queue, resize_queue)
resize_threads = start_threads(8, resize, resize_queue, upload_queue)
upload_threads = start_threads(8, upload, upload_queue, done_queue)

for _ in range(1000):
    download_queue.put(_)

stop_threads(download_queue, download_threads)
stop_threads(resize_queue, resize_threads)
stop_threads(upload_queue, upload_threads)

print(done_queue.qsize(), "items finished")
end = time.time()
delta = end - start
print(f"Took {delta:.3f} seconds")

# %%
