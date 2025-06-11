import sys
import socket
import json

NB_DEP = 10

def send_to(player_id, dx, dy):
    for p in ports_send:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((ip, p))
                data = json.dumps([player_id, dx, dy])
                s.send(data.encode())
            except Exception as e:
                print(f"Error sending data to port_listen {p}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage : server.py local_port port1 port2 port3")
        sys.exit(0)

    port_listen = int(sys.argv[1])
    ports_send = [int(txt) for txt in sys.argv[2:]]
    nb_ports = len(ports_send)

    ip = "localhost"

    print("\nListening port_listen =", port_listen)
    print("Sending ports_send =", ports_send)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(('', port_listen))
        print("\n=== Start Server ===")
        for i in range(nb_ports * NB_DEP):
            server_socket.listen()
            client_connect, address_client = server_socket.accept()
            with client_connect:
                print(address_client, "connected")
                res = client_connect.recv(255).decode("utf-8")
                lst = json.loads(res)
                send_to(lst[0], lst[1], lst[2])
        
    print("=== End Server ===")
