# ./zellij --layout layout_server_naimi.kdl

import sys
import socket
import json
import threading

IP = "localhost"
NB_DEP = 10

TOKEN = "TOKEN"
REQUEST = "REQUEST"
STANDARD = "STANDARD"
STOP = "STOP"

lock = threading.Lock()

list_action = []
etat = STANDARD
parent = 0
list_request = []
nb_dep_total = 0

stop_event = threading.Event()  # Événement pour signaler l'arrêt


def sendToMonitors(player_id, dx, dy):
    for p in LIST_PLAYER:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((IP, p))
                data = json.dumps([player_id, dx, dy])
                s.send(data.encode())
            except Exception as e:
                print(f"Send error to {p}: {e}")

def sendMsg(send_server, msg):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((IP, send_server))
            s.send(msg.encode())
        except Exception as e:
            print(f"[Error] sending {msg} to {send_server}: {e}")


def handle_state():
    global etat, list_action, parent, list_request, nb_dep_total

    with lock:
        if etat == STANDARD:
            if list_action:                
                msg_send = json.dumps([REQUEST, NUM_PLAYER])
                sendMsg(LIST_SERVER[parent], msg_send)
                etat = REQUEST
        
        elif etat == TOKEN and not list_action and list_request:
            parent = list_request.pop(0)
            msg_send = json.dumps([TOKEN, list_request, nb_dep_total])
            sendMsg(LIST_SERVER[parent], msg_send)
            etat = STANDARD
        elif etat == TOKEN:
            if nb_dep_total == NB_DEP*NB_PLAYER:
                for s in LIST_SERVER:
                    msg_send = json.dumps([STOP])
                    sendMsg(s, msg_send)
        elif etat == STOP:
            print("STOP SERVER")
            stop_event.set() 

        

def handle_send():
    global etat, list_action, parent, list_request, nb_dep_total
    
    with lock:
        if etat == TOKEN and list_action:
            for a in list_action[:]:
                sendToMonitors(a[0], a[1], a[2])
                nb_dep_total += 1
            list_action.clear()

def handle_receive(client_socket):
    global etat, parent, list_request, list_action, nb_dep_total

    
    with lock:
        data = client_socket.recv(1024).decode("utf-8")
        msg = json.loads(data)
        print(f"{address_client} connected, message received : {data}.")
        
        if msg[0] == TOKEN:  # Format message : [TOKEN, [X,X,X], nb_dep_total]
            if etat == REQUEST:
                etat = TOKEN
                parent = NUM_PLAYER
                list_request = msg[1]
                nb_dep_total = msg[2]
            else:
                print("Received a TOKEN but not used")
         
        elif msg[0] == REQUEST:  # Format message : [REQUEST, num_player_send]
            if etat == TOKEN:
                list_request.append(msg[1])
            elif etat in [REQUEST, STANDARD]:
                msg_send = json.dumps(msg)
                sendMsg(LIST_SERVER[parent], msg_send)
            
        elif msg[0] == STOP: # Format message : [STOP]
            etat = STOP

        else:  # Format message : [player_id, id_x, id_y]
            list_action.append(msg)


if __name__ == "__main__":
    if len(sys.argv) < 6:
        print(f"[Usage] {sys.argv[0]} nb_player num_player port_monitor<0 .. nb_player-1> port_server_jeton<0 .. nb_player-1>")
        sys.exit(1)

    NB_PLAYER = int(sys.argv[1])
    NUM_PLAYER = int(sys.argv[2])

    if len(sys.argv) < 3 + NB_PLAYER + 2:
        print(f"[Error] Insufficient number of arguments for {NB_PLAYER} players.")
        sys.exit(1)

    LIST_SERVER = [int(txt) for txt in sys.argv[3 + NB_PLAYER:]]
    LIST_PLAYER = [int(txt) for txt in sys.argv[3:3 + NB_PLAYER]]
    PORT_SERVER = LIST_SERVER[NUM_PLAYER]

    if NUM_PLAYER == 0:
        etat = TOKEN
        

    print(f"\nPlayer {NUM_PLAYER} server {PORT_SERVER}")
    print(f"Player ports list: {LIST_PLAYER}")
    print(f"Server ports list: {LIST_SERVER}")
    print("=====\n")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('', PORT_SERVER))
    server_socket.listen(5)
    print(f"Start server on {NUM_PLAYER}:{PORT_SERVER}")

    while not stop_event.is_set():

        client_socket, address_client = server_socket.accept()

        # Lancer les threads
        receive_thread = threading.Thread(target=handle_receive, args=(client_socket,))
        send_thread = threading.Thread(target=handle_send)
        state_thread = threading.Thread(target=handle_state)

        receive_thread.start()
        send_thread.start()
        state_thread.start()

        # Attendre la fin des threads
        receive_thread.join()
        send_thread.join()
        state_thread.join()

    server_socket.close()
    print(f"\n=== End of server {NUM_PLAYER} ===")