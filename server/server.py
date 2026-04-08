import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import shared.protocol as protocol 

import socket
import threading

# 0.0.0.0 inseamna ca serverul va accepta conexiuni de pe orice interfata de retea
HOST = '0.0.0.0'
PORT = 5000

# Dictionar pentru a pastra clientii activi. Format: {"nume_utilizator": obiect_socket}
connected_users = {}
# Un Lock este esential aici pentru a preveni crash-urile la accesari simultane din thread-uri diferite
users_lock = threading.Lock()

def broadcast(metadata, exclude_user=None):
    """Trimite un mesaj catre toti utilizatorii conectati, util pentru notificari globale."""
    with users_lock:
        for username, client_socket in connected_users.items():
            if username != exclude_user:
                try:
                    protocol.send_msg(client_socket, metadata)
                except:
                    pass

def handle_client(client_socket, address):
    """Functia care ruleaza intr-un thread separat pentru FIECARE client conectat."""
    print(f"[+] Conexiune noua initiata de la {address}")
    username = None

    try:
        # 1. Handshake-ul initial. Asteptam ca primul mesaj sa fie cererea de autentificare.
        metadata, _ = protocol.recv_msg(client_socket)
        
        if not metadata or metadata.get("type") != "connect":
            print(f"[-] Clientul {address} nu a respectat protocolul de conectare.")
            return

        username = metadata.get("username")

        with users_lock:
            # 2. Validam unicitatea numelui de utilizator
            if username in connected_users:
                print(f"[-] Numele '{username}' e deja folosit. Respingem conexiunea.")
                protocol.send_msg(client_socket, {"type": "connect_ack", "status": "deny", "reason": "Numele este deja utilizat."})
                return
            
            # 3. Autentificare reusita. Trimitem lista cu cine este deja online.
            current_users = list(connected_users.keys())
            protocol.send_msg(client_socket, {"type": "connect_ack", "status": "accept", "users": current_users})
            
            # Il inregistram in sistem
            connected_users[username] = client_socket

        print(f"[+] '{username}' s-a autentificat cu succes.")

        # 4. Notificam restul retelei ca a aparut cineva nou
        broadcast({"type": "user_joined", "username": username}, exclude_user=username)

        # 5. Bucla principala de ascultare pentru acest client
        while True:
            meta, binary_data = protocol.recv_msg(client_socket)
            
            if not meta:
                break 

            # Daca pachetul este destinat altui utilizator (cerere stream sau frame video)
            if meta.get("type") in ["request_stream", "frame"]:
                target_user = meta.get("target")
                
                with users_lock:
                    if target_user in connected_users:
                        target_socket = connected_users[target_user]
                        protocol.send_msg(target_socket, meta, binary_data)
                    else:
                        print(f"[!] '{username}' a trimis pachet pentru '{target_user}', dar tinta s-a deconectat.")

    except Exception as e:
        print(f"[!] Eroare de retea cu {username} ({address}): {e}")

    finally:
        # 6. Curatenie la deconectare
        client_socket.close()
        if username:
            with users_lock:
                if username in connected_users:
                    del connected_users[username]
            print(f"[-] '{username}' s-a deconectat.")
            broadcast({"type": "user_left", "username": username})

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"[*] Serverul a pornit si asculta pe portul {PORT}...")

    try:
        while True:
            client_socket, address = server.accept()
            client_thread = threading.Thread(target=handle_client, args=(client_socket, address))
            client_thread.daemon = True
            client_thread.start()
    except KeyboardInterrupt:
        print("\n[*] Oprire server ceruta de utilizator (Ctrl+C).")
    finally:
        server.close()

if __name__ == "__main__":
    start_server()