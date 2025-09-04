# client.py
import socket
import threading

SERVER_HOST = '127.0.0.1'  # change to server IP if connecting across LAN
SERVER_PORT = 5555

def receive_messages(sock):
    while True:
        try:
            data = sock.recv(1024).decode()
            if not data:
                print("\n[DISCONNECTED] Server closed connection.")
                break
            # print received message and re-show prompt
            print("\r" + data + "\n> ", end="")
        except:
            break

def main():
    username = input("Choose a username: ").strip()
    if not username:
        print("Username required.")
        return

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((SERVER_HOST, SERVER_PORT))
    except ConnectionRefusedError:
        print("Could not connect to server. Is it running?")
        return

    # send username as first message
    sock.send(username.encode())

    recv_thread = threading.Thread(target=receive_messages, args=(sock,), daemon=True)
    recv_thread.start()

    print("Connected! Type messages and press Enter. Type /quit to exit.")
    try:
        while True:
            msg = input("> ")
            if msg.strip() == "":
                continue
            sock.send(msg.encode())
            if msg.strip() == "/quit":
                break
    except KeyboardInterrupt:
        sock.send("/quit".encode())
    finally:
        sock.close()
        print("Disconnected.")

if __name__ == "__main__":
    main()
