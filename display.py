#!/usr/bin/env python3
import argparse
import curses
import socket
import json
import random
import hashlib
from curses import wrapper
from sprites_bomb import bomb_sprite, player_sprite

BOARD_WIDTH = 10
BOARD_HEIGHT = 10
BOMB_DROP_DELAY = 3  # every 3 turns

class Game:
    def __init__(self, nb_players=2, max_turns=10, seed=42):
        self.nb_players = nb_players
        self.turns = 0
        self.max_turns = max_turns*self.nb_players
        self.players = [(BOARD_HEIGHT - 1, i * (BOARD_WIDTH // nb_players)) for i in range(nb_players)]
        self.scores = [0] * self.nb_players
        self.bombs = []  # list of (x, y)
        self.logs = []
        random.seed(seed)

    def drop_bomb(self):
        x = 0
        y = random.randint(0, BOARD_WIDTH - 1)
        self.bombs.append([x, y])

    def move_player(self, pid, dx):
        x, y = self.players[pid]
        y = (y + dx) % BOARD_WIDTH
        self.players[pid] = (x, y)

    def update(self):
        new_bombs = []
        for x, y in self.bombs:
            x += 1
            if x >= BOARD_HEIGHT:
                continue
            caught = False
            for pid, (px, py) in enumerate(self.players):
                if x == px and y == py:
                    self.scores[pid] += 1
                    caught = True
                    break
            if not caught:
                new_bombs.append([x, y])
        self.bombs = new_bombs

def draw(stdscr, game):
    stdscr.clear()
    board = [[" " for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
    for x, y in game.bombs:
        if 0 <= x < BOARD_HEIGHT and 0 <= y < BOARD_WIDTH:
            board[x][y] = bomb_sprite
    for idx, (x, y) in enumerate(game.players):
        board[x][y] = str(idx)

    for i, row in enumerate(board):
        stdscr.addstr(i, 0, "".join(row))
    stdscr.addstr(BOARD_HEIGHT + 1, 0, "Scores: " + str(game.scores))
    stdscr.refresh()

def recv_json(sock):
    data = ''
    while True:
        part = sock.recv(1024)
        if part == b'':
            break
        data += part.decode()
    return json.loads(data)

def main(stdscr):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('', port))
        server.listen(5)

        for _ in range(game.max_turns):
            if game.turns % BOMB_DROP_DELAY == 0:
                game.drop_bomb()
            draw(stdscr, game)

            client, _ = server.accept()
            move = recv_json(client)
            pid, dx, dy = move
            game.move_player(pid, dx)
            game.update()
            game.logs.append(move)
            game.turns += 1
        stdscr.clear()
        print("END")
        draw(stdscr, game)
        stdscr.refresh()

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--port', type=int, default=9000)
parser.add_argument('-n', '--players', type=int, default=2)
args = parser.parse_args()

port = args.port
game = Game(nb_players=args.players)

wrapper(main)
print(game.logs)
print(game.scores)

for pos in range(args.players):
    for (i, _,_) in game.logs:
        if i == pos:
            print("█", end="")
        else:
            print(" ", end="")
    print("")

dhash = hashlib.md5()
encoded = json.dumps(game.logs).encode()
dhash.update(encoded)
print(dhash.hexdigest())
