import sys
import socket
import json

RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
BLUE = "\033[34m"
YELLOW = "\033[33m"
MAGENTA = "\033[35m"

NO_CLIENT_TIMEOUT = 2
IP = "localhost"
NB_DEP = 10

def updateVectorClock(local_clock, received_clock):
    for i in range(len(local_clock)):
        local_clock[i] = max(local_clock[i], received_clock[i])

def hasPriorityOver(local_clock, received_clock):
    for i in range(len(local_clock)):
        if local_clock[i] <= received_clock[i]:
            return True  # local_clock a la priorité
        elif local_clock[i] > received_clock[i]:
            return False  # received_clock a la priorité


def sendMsg(port, msg):
    # Fonction pour envoyer des messages aux autres serveurs
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((IP, port))
            s.sendall(msg.encode()) 
        except Exception as e:
            print(f"{RESET}[Error] Failed to send to {port}: {e}")

def sendToMonitors(player_id, dx, dy):
    for p in list_ports_player:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((IP, p))
                data = json.dumps([player_id, dx, dy])
                s.sendall(data.encode())
            except Exception as e:
                print(f"{RESET}Send error to monitor {p}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 6:
        print(f"[Usage] {sys.argv[0]} nb_player num_player port_monitor<0 .. nb_player-1> port_server<0 .. nb_player-1>")
        sys.exit(1)

    nb_player = int(sys.argv[1])
    num_player = int(sys.argv[2])

    if len(sys.argv) < 3 + nb_player + 2:
        print(f"[Error] Insufficient arguments for {nb_player} players.")
        sys.exit(1)

    list_ports_server = [int(p) for p in sys.argv[3 + nb_player:]]
    list_ports_player = [int(p) for p in sys.argv[3:3 + nb_player]]
    port_player = list_ports_server[num_player]

    list_action = []                # Liste des actions recues et où une demande REQUEST a été envoyée
    list_action_waiting = []        # Liste des actions recues pendant une SC ou si une demande REQUEST 
    vector_clock = [0] * nb_player  # Horloge Mattern globale
    my_request_clock = None         # Mon horloge au moment de l'envoi du REQUEST
    list_waiting_request = set()    # Liste des serveurs en attente d'une réponse à leur REQUEST
    list_waiting_replies = set()    # Liste des serveurs où on attend leur réponse REPLY
    list_stop = set()               # Liste des serveurs qui ont fini leur exécution
    requested = False               # En attente des réponses REPLY des autres serveurs
    critical_section = False
    running = True
    count = 0                       # Nombre de déplacement PLAYER reçu
    send_stop = False               # A déjà envoyé un STOP aux autres serveurs


    print(f"\nPlayer {num_player} server")
    print(f"Player ports list: {list_ports_player}")
    print(f"Server ports list: {list_ports_server}")
    print(f"Global vectorial clock: {vector_clock}")
    print("=====\n")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("", port_player))
    server_socket.listen()

    try:
        while running:
            client_connect, address_client = server_socket.accept()

            with client_connect:
                res = client_connect.recv(1024).decode("utf-8")
                msg = json.loads(res)

                match msg[0]:
                    case "REQUEST":
                        print(f"{BLUE}[RECEIVE] [REQUEST P{msg[1]}]")
                        num_sender = msg[1]
                        received_clock = msg[2]
                        vector_clock[num_player] += 1
                        updateVectorClock(vector_clock, received_clock)
                        
                        if (not critical_section and requested and hasPriorityOver(received_clock, my_request_clock)) or not requested:
                            vector_clock[num_player] += 1
                            print(f"{GREEN}[SEND] [REPLY P{num_sender}]{RESET}")
                            reply_msg = json.dumps(["REPLY", num_player, vector_clock.copy()])
                            sendMsg(list_ports_server[num_sender], reply_msg)
                        else:
                            list_waiting_request.add(num_sender)


                    case "REPLY":
                        print(f"{BLUE}[RECEIVE] [REPLY P{msg[1]}]")
                        num_sender = msg[1]
                        received_clock = msg[2]
                        vector_clock[num_player] += 1
                        updateVectorClock(vector_clock, received_clock)
                        
                        list_waiting_replies.discard(num_sender)

                        if not list_waiting_replies:
                            critical_section = True
                            requested = False
                            my_request_clock = None

                            print(f"{RED}----[SC ENTER]----")

                            for a in list_action[:]:
                                count += 1
                                sendToMonitors(a[0], a[1], a[2])
                                print(f"{YELLOW}[SEND][PLAYER]{a}")
                            list_action.clear()

                            critical_section = False
                            print(f"{RED}----[SC  EXIT]----")

                            # Répondre aux demandes en attente
                            for p in list_waiting_request:
                                vector_clock[num_player] += 1
                                reply_msg = json.dumps(["REPLY", num_player, vector_clock.copy()])
                                print(f"{GREEN}[SEND] [REPLY P{p}]")
                                sendMsg(list_ports_server[p], reply_msg)
                            list_waiting_request.clear()

                            # S'il y a eu des réceptions de messages en parallèle de la section critique, alors envoyé un REQUEST pour la nouvelle liste
                            if list_action_waiting:
                                for i in list_action_waiting[:]:
                                    list_action.append(i)
                                requested = True
                                vector_clock[num_player] += 1
                                my_request_clock = vector_clock.copy()
                                msg_send = json.dumps(["REQUEST", num_player, my_request_clock])
                                print(f"{GREEN}[SEND] [REQUEST ALL P]")
                                
                                list_waiting_replies = set(range(nb_player)) - {num_player}
                                for i, port in enumerate(list_ports_server):
                                    if i != num_player:
                                        sendMsg(port, msg_send)
                            list_action_waiting.clear()
                    
                    case "STOP":
                        print(f"{MAGENTA}[RECEIVE][STOP P{msg[1]}]")
                        list_stop.add(msg[1])

                    case _:
                        try:
                            print(f"{YELLOW}[RECEIVE][PLAYER]{msg}")
                            if not requested and not critical_section:
                                list_action.append(msg)
                                requested = True
                                vector_clock[num_player] += 1
                                my_request_clock = vector_clock.copy()
                                msg_send = json.dumps(["REQUEST", num_player, my_request_clock])
                                print(f"{GREEN}[SEND] [REQUEST ALL P]")

                                list_waiting_replies = set(range(nb_player)) - {num_player}
                                for i, port in enumerate(list_ports_server):
                                    if i != num_player:
                                        sendMsg(port, msg_send)
                            else:
                                list_action_waiting.append(msg)

                        except json.JSONDecodeError:
                            print(f"{RESET}[Error] Invalid data received: {res}")
        
            # Gérer la fermeture du serveur
            if count == NB_DEP:
                if not send_stop:
                    msg_send = json.dumps(["STOP", num_player,])
                    print(f"{MAGENTA}[SEND] [STOP ALL P]")
                                            
                    for i, port in enumerate(list_ports_server):
                        if i != num_player:
                            sendMsg(port, msg_send)
                    send_stop = True

                if len(list_stop) == nb_player-1:
                    running = False

    except KeyboardInterrupt:
        print(f"{RESET}\nInterruption detected, shutting down the server...")

    finally:
        server_socket.close()
        print(f"{RESET}\n\n=== End of server {num_player} ===")
