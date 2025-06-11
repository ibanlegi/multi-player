# ./zellij --layout layout_server_jeton.kdl

import time
import sys
import socket
import json

NO_CLIENT_TIMEOUT = 2
IP = "localhost"

def send_to(player_id, dx, dy):
    for p in LIST_PLAYER:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((IP, p))
                data = json.dumps([player_id, dx, dy])
                s.send(data.encode())
            except Exception as e:
                print(f"Send error to {p}: {e}")

def send_msg(send_next, msg):
    print(f"Sending {msg} to the server {send_next}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((IP, send_next))
            s.send(msg.encode())
            print(f"{msg} successfully sent to {IP}:{send_next}")
        except Exception as e:
            print(f"[Error] sending {msg} to {send_next}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 6:
        print(f"[Usage] {sys.argv[0]} nb_player num_player port_monitor<0 .. NB_PLAYER-1> port_server_jeton<0 .. NB_PLAYER-1>")
        sys.exit(1)

    NB_PLAYER = int(sys.argv[1])
    NUM_PLAYER = int(sys.argv[2])

    if len(sys.argv) < 3 + NB_PLAYER + 2:
        print(f"[Error] Insufficient number of arguments for {NB_PLAYER} players.")
        sys.exit(1)

    LIST_SERVER = [int(txt) for txt in sys.argv[3 + NB_PLAYER:]]
    LIST_PLAYER = [int(txt) for txt in sys.argv[3:3 + NB_PLAYER]]
    PORT_SERVER = LIST_SERVER[NUM_PLAYER]

    
    list_action = []
    token = False
    token_start = False
    stop_signal_received = False  # Indique si un serveur a déjà reçu STOP
    running = True                # Flag pour contrôler l'exécution
    last_message_time = None      # Temps du dernier message classique reçu

    print(f"\nPlayer {NUM_PLAYER}'s server")
    print(f"Player ports list: {LIST_PLAYER}")
    print(f"Server ports list: {LIST_SERVER}")
    print("=====\n")


    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('', PORT_SERVER))
    server_socket.listen()

    try:
        if NUM_PLAYER == 0:
            time.sleep(0.5)
            send_msg(LIST_SERVER[(NUM_PLAYER + 1) % NB_PLAYER], "TOKEN_START")  # Envoi initial du jeton

        while running:
            server_socket.settimeout(NO_CLIENT_TIMEOUT)  # Applique un timeout pour détecter l'inactivité

            try:
                client_connect, address_client = server_socket.accept()
                with client_connect:
                    res = client_connect.recv(1024).decode("utf-8")
                    print(f"{address_client} connected, message received : {res}.")

                    match res:
                        case "TOKEN_START":
                            token = True
                            token_start = True
                            print("Startup TOKEN successfully received.")

                        case "TOKEN":
                            token = True
                            token_start = False
                            last_message_time = time.time()
                            print("TOKEN successfully received.")

                        case "STOP":
                            if stop_signal_received:
                                print(f"Server {NUM_PLAYER} receives a second STOP, immediate shutdown.")
                                running = False
                                break
                            stop_signal_received = True
                            print(f"STOP received.")

                        case _:
                            try:
                                action = json.loads(res)
                                list_action.append(action)
                                last_message_time = time.time()
                            except json.JSONDecodeError:
                                print(f"[Error] Invalid data received : {res}")

            except socket.timeout:
                # Vérifie si le serveur a le token mais n'a reçu aucune action depuis un moment
                if token and not token_start and (last_message_time is None or time.time() - last_message_time > NO_CLIENT_TIMEOUT):
                    stop_signal_received = True
                    send_msg(LIST_SERVER[(NUM_PLAYER + 1) % NB_PLAYER], "STOP")
                    print(f"Server {NUM_PLAYER} has no more actions, sending STOP and shutting down.")
                    running = False  # Arrêt du serveur
                    break
                continue

            # Traitement des actions si on a le token
            if token and list_action:
                for a in list_action[:]:
                    send_to(a[0], a[1], a[2])
                list_action.clear()

                # Si un arrêt est demandé, on envoie STOP après traitement
                if stop_signal_received:
                    send_msg(LIST_SERVER[(NUM_PLAYER + 1) % NB_PLAYER], "STOP")
                    print(f"Server {NUM_PLAYER} finishes its actions and sends STOP to the next one.")
                    running = False
                    break
                else:
                    send_msg(LIST_SERVER[(NUM_PLAYER + 1) % NB_PLAYER], "TOKEN")

                token = False

            # Si le serveur a reçu STOP et n'a plus rien à faire, il arrête
            if stop_signal_received and not token and not list_action:
                send_msg(LIST_SERVER[(NUM_PLAYER + 1) % NB_PLAYER], "STOP")
                print(f"Server {NUM_PLAYER} is done and sends STOP to the next one, shutting down.")
                running = False
                break

    except KeyboardInterrupt:
        print("\nInterruption detected, shutting down the server...")

    finally:
        server_socket.close()
        print(f"=== End of server {NUM_PLAYER} ===")
