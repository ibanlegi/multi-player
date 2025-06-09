import socket
import sys
import random
import json
import time

NB_DEP = 10

def send_move(pid, dx):
    for p in ports:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, p))
                data = json.dumps([pid, dx, 0])
                s.send(data.encode())
        except:
            continue

if len(sys.argv) < 3:
    print("Usage: player.py PLAYER_ID PORT1 [PORT2...]")
    sys.exit(1)

player_id = int(sys.argv[1])
ports = [int(p) for p in sys.argv[2:]]
host = "localhost"
random.seed(42 + player_id)

for _ in range(NB_DEP):
    dx = random.choice([-1, 0, 1])  # left, stay, right
    send_move(player_id, dx)
    #time.sleep(0.1)
