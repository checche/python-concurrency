"""
subprocessでOSコマンドをサブプロセス(子プロセス)で実行
subprocess.run(): サブプロセスの実行

subprocess.Popen: サブプロセスの実行をより高度に行う
Popen.poll(): サブプロセスの状態をポーリングする
Popen.communicate():
    実行終了を待つ。
    標準出力/エラーを返す事ができる。
    timeoutで実行時間に制限をかけられる。
"""

# %%
import os
import subprocess
import time

# %%
# シェルの実行
result = subprocess.run(
    ["echo", "Hello from the child"], capture_output=True, encoding="utf-8"
)

result.check_returncode()
print(result.stdout)


# %%
# Popenも実行するコマンド。ポーリング等ができる
proc = subprocess.Popen(["sleep", "1"])
while proc.poll() is None:
    print("Working...")

print("Exit status", proc.poll())


# %%
start = time.time()
sleep_procs = []
for _ in range(10):
    proc = subprocess.Popen(["sleep", "1"])
    sleep_procs.append(proc)

# communicate()で終了を待つことができる
for proc in sleep_procs:
    proc.communicate()

end = time.time()
delta = end - start
print(f"Finished in {delta:.3} seconds")


# %%
# パイプをつかって標準入出力を利用できる
def run_encrypt(data) -> subprocess.Popen:
    env = os.environ.copy()
    env["password"] = "aaaaaaaaaaaa"
    proc = subprocess.Popen(
        ["openssl", "enc", "-des3", "-pass", "env:password"],
        env=env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )

    proc.stdin.write(data)
    proc.stdin.flush()  # 入力の確定(バッファの開放)
    return proc


procs = []
for _ in range(3):
    data = os.urandom(10)
    proc = run_encrypt(data)
    procs.append(proc)

# communicateで処理を待ち、出力を受け取る事ができる
for proc in procs:
    out, _ = proc.communicate()
    print(out[-10:])


# %%
# パイプの連鎖処理
def run_hash(input_stdin) -> subprocess.Popen:
    return subprocess.Popen(
        ["openssl", "dgst", "-whirlpool", "-binary"],
        stdin=input_stdin,
        stdout=subprocess.PIPE,
    )


encrypt_procs = []
hash_procs = []

for _ in range(3):
    data = os.urandom(100)

    encrypt_proc = run_encrypt(data)
    encrypt_procs.append(encrypt_proc)
    hash_proc = run_hash(encrypt_proc.stdout)
    hash_procs.append(hash_proc)

    # ストリームを閉じる
    encrypt_proc.stdout.close()
    encrypt_proc.stdout = None

for proc in encrypt_procs:
    out, _ = proc.communicate()
    print(out)  # Noneになる
    assert proc.returncode == 0

for proc in hash_procs:
    out, _ = proc.communicate()
    print(out[-10:])
    assert proc.returncode == 0


# %%
# 実行時間に制限をかける
proc = subprocess.Popen(["sleep", "10"])
try:
    proc.communicate(timeout=0.1)
except subprocess.TimeoutExpired:
    proc.terminate()
    proc.wait()
    print("Exit status", proc.poll())

# %%
