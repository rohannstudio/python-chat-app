# server.py
import socket
import threading

HOST = '0.0.0.0'   # listen on all interfaces (use '127.0.0.1' for local-only)
PORT = 5555

clients = []  # list of tuples: (conn, addr, username)
clients_lock = threading.Lock()

def broadcast(message, exclude_conn=None):
    with clients_lock:
        for conn, addr, username in clients:
            if conn is not exclude_conn:
                try:
                    conn.send(message.encode())
                except:
                    pass

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr}")
    username = None
    try:
        # first message expected: username
        username = conn.recv(1024).decode().strip()
        if not username:
            conn.close()
            return
        with clients_lock:
            clients.append((conn, addr, username))

        join_msg = f"*** {username} has joined the chat ***"
        print(join_msg)
        broadcast(join_msg, exclude_conn=conn)
        conn.send("You are connected. Type /quit to exit.\n".encode())

        while True:
            data = conn.recv(1024).decode()
            if not data:
                break
            if data.strip() == "/quit":
                break
            message = f"{username}: {data}"
            print(message)
            broadcast(message, exclude_conn=conn)
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        # remove client
        with clients_lock:
            for i, (c, a, u) in enumerate(clients):
                if c is conn:
                    clients.pop(i)
                    break
        if username:
            leave_msg = f"*** {username} has left the chat ***"
            print(leave_msg)
            broadcast(leave_msg, exclude_conn=None)
        conn.close()

def start():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[STARTED] Server listening on {HOST}:{PORT}")
    try:
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            thread.start()
    except KeyboardInterrupt:
        print("\n[SHUTTING DOWN] Server closing")
    finally:
        server.close()

if __name__ == "__main__":
    start()
