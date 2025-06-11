# ./zellij --layout layout_server_maekawa.kdl

import sys
import socket
import json
import threading
import time

IP = "localhost"
NB_DEP = 10

DEMANDE = "DEMANDE"
ACCORD = "ACCORD"
LIBERATION = "LIBERATION"
STOP = "STOP"
CRITICAL = "CRITICAL"
STANDARD = "STANDARD"
ECHEC = "ECHEC"
SONDAGE = "SONDAGE"
RESTITUTION = "RESTITUTION"

lock = threading.Lock()
stop_event = threading.Event()


state = STANDARD
QUORUM = set()
list_waiting = []
list_action = []
nb_responses = 0
nb_dep = 0
nb_stop = 0
lamport_clock = 0 
vote_given_to = None
last_vote_time = None
sondage_sent = False
stop_sent = False

def is_prioritized(request1, request2):

    return request1 < request2

def sendMsg(send_server, msg):
    global lamport_clock 

    lamport_clock += 1 

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((IP, send_server))
            s.send(msg.encode())
        except Exception as e:
            print(f"[{NUM_PLAYER}] Erreur d'envoi à {send_server}: {e}")

def sendToMonitors(player_id, dx, dy):
    global lamport_clock

    lamport_clock += 1  

    for p in LIST_PLAYER:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((IP, p))
                data = json.dumps([player_id, dx, dy])
                s.send(data.encode())
            except Exception as e:
                print(f"[{NUM_PLAYER}] Erreur d'envoi à {p}: {e}")

def requestAccess():
    global nb_responses, state, lamport_clock

    print(f"[{NUM_PLAYER}] Demande d'accès envoyée à {QUORUM} (Clock: {lamport_clock})") 
    nb_responses = 0
    lamport_clock += 1  
    timestamp = lamport_clock

    for p in QUORUM:
        sendMsg(LIST_SERVER[p], json.dumps([DEMANDE, NUM_PLAYER, timestamp]))
    state = DEMANDE

def handle_state():
    global state, nb_responses, lamport_clock, nb_dep, nb_stop, stop_sent

    with lock:

        if state == STANDARD and list_action:
            print(f"[{NUM_PLAYER}] Passé à l'état DEMANDE (Clock: {lamport_clock})")
            requestAccess()

        elif state == DEMANDE and nb_responses == len(QUORUM):
            print(f"[{NUM_PLAYER}] => Accès à la ressource autorisé (Clock: {lamport_clock})")  
            state = CRITICAL

        elif state == CRITICAL:
            for a in list_action[:]:
                sendToMonitors(a[0], a[1], a[2])
                nb_dep += 1
            list_action.clear()

            time.sleep(0.1)

            for p in QUORUM:
                sendMsg(LIST_SERVER[p], json.dumps([LIBERATION, NUM_PLAYER]))
            
            if nb_dep == NB_DEP and not stop_sent:
                for p in QUORUM:
                    sendMsg(LIST_SERVER[p], json.dumps([STOP]))
                stop_sent = True

            state = STANDARD

        if nb_stop == len(QUORUM):
            print("STOP SERVER")
            stop_event.set()

def handle_receive(client_socket):
    global vote_given_to, list_waiting, nb_responses, list_action, last_vote_time, sondage_sent, lamport_clock, nb_stop
    
    with client_socket:
        data = client_socket.recv(1024).decode("utf-8")
        msg = json.loads(data)
        print(f"[{NUM_PLAYER}] Message reçu: {msg} (Clock: {lamport_clock})")

        with lock:
            # Mise à jour de l'horloge Lamport
            if msg[0] == DEMANDE: # Format : [DEMANDE, num_sender, h_sender]
                h_requester = msg[2]
                requester = msg[1]
                print(f"[{NUM_PLAYER}] DEMANDE reçue de {requester} avec timestamp {h_requester} (Clock: {lamport_clock})")  
                received_request = (h_requester, requester)
                if vote_given_to is None:
                    vote_given_to = requester
                    last_vote_time = received_request
                    sendMsg(LIST_SERVER[requester], json.dumps([ACCORD, NUM_PLAYER]))
                    print(f"[{NUM_PLAYER}] Accord envoyé à {requester} (Clock: {lamport_clock})") 
                else:
                    if is_prioritized(received_request, last_vote_time):
                        if not sondage_sent:
                            sendMsg(LIST_SERVER[vote_given_to], json.dumps([SONDAGE, NUM_PLAYER]))
                            sondage_sent = True
                        list_waiting.append(received_request)
                    else:
                        sendMsg(LIST_SERVER[requester], json.dumps([ECHEC, NUM_PLAYER]))
                        list_waiting.append(received_request)

            elif msg[0] == ACCORD: # Format : [ACCORD, num_sender]
                nb_responses += 1
                print(f"[{NUM_PLAYER}] Réponse reçue de {msg[1]} : {nb_responses}/{len(QUORUM)} (Clock: {lamport_clock})")

            elif msg[0] == LIBERATION: # Format : [LIBERATION, num_sender]
                print(f"[{NUM_PLAYER}] La ressource a été libérée par {msg[1]} (Clock: {lamport_clock})")
                vote_given_to = None
                sondage_sent = False
                if list_waiting:
                    list_waiting.sort()
                    next = list_waiting.pop(0)
                    vote_given_to = next[1]
                    last_vote_time = next
                    sendMsg(LIST_SERVER[vote_given_to], json.dumps([ACCORD, NUM_PLAYER]))

            elif msg[0] == ECHEC: # Format : [ECHEC, num_sender]
                pass

            elif msg[0] == SONDAGE: # Format : [SONDAGE, num_sender]
                if state == DEMANDE:
                    sendMsg(LIST_SERVER[msg[1]], json.dumps([RESTITUTION, NUM_PLAYER]))
                    print(f"[{NUM_PLAYER}] Sondage répondu à {msg[1]} (Clock: {lamport_clock})")

            elif msg[0] == RESTITUTION: # Format : [RESTITUTION, num_sender]
                sondage_sent = False
                if list_waiting:
                    list_waiting.sort()
                    next = list_waiting.pop(0)
                    vote_given_to = next[1]
                    last_vote_time = next
                    sendMsg(LIST_SERVER[vote_given_to], json.dumps([ACCORD, NUM_PLAYER]))
            
            elif msg[0] == STOP: 
                nb_stop += 1

            else:  # == ACTION PALYER   # Format : [id, d_x, d_y]
                list_action.append(msg)
                if state == STANDARD:
                    print(f"[{NUM_PLAYER}] Action en file d'attente, appel à requestAccess (Clock: {lamport_clock})")
                    requestAccess()

def state_loop():
    while not stop_event.is_set():
        handle_state()
        time.sleep(0.1)

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.settimeout(1.0)
    server_socket.bind(('', PORT_SERVER))
    server_socket.listen(5)

    print(f"Start server on {NUM_PLAYER}:{PORT_SERVER}")
    threading.Thread(target=state_loop, daemon=True).start()

    while not stop_event.is_set():
        try:
            client_socket, addr = server_socket.accept()
            threading.Thread(target=handle_receive, args=(client_socket,), daemon=True).start()
        except socket.timeout:
            continue
        except Exception as e:
            print(f"Erreur d'acceptation de connexion : {e}")
            break

    server_socket.close()
    print(f"\n=== Fin du serveur {NUM_PLAYER} ===")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"[Usage] {sys.argv[0]} nb_player num_player port_monitor<0 .. nb_player-1> port_server<0 .. nb_player-1>")
        sys.exit(1)

    NB_PLAYER = int(sys.argv[1])
    NUM_PLAYER = int(sys.argv[2])

    if len(sys.argv) < 3 + NB_PLAYER + 2:
        print(f"[Error] Not enough arguments for {NB_PLAYER} players.")
        sys.exit(1)

    LIST_PLAYER = [int(txt) for txt in sys.argv[3:3 + NB_PLAYER]]
    LIST_SERVER = [int(txt) for txt in sys.argv[3 + NB_PLAYER:]]
    PORT_SERVER = LIST_SERVER[NUM_PLAYER]

    QUORUM = set([(NUM_PLAYER + i) % NB_PLAYER for i in range(3)])

    print(f"\nPlayer {NUM_PLAYER} — server {PORT_SERVER}")
    print(f"Quorum : {QUORUM}")
    print(f"=====\n")

    start_server()
