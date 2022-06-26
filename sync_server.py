import socket
from socket import AF_INET, SOCK_STREAM


def serve(host, port):
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind((host, port))
    serversocket.listen(5)

    while True:
        (clientsocket, address) = serversocket.accept()
        print(clientsocket, address)

        with clientsocket:
            while True:
                data = clientsocket.recv(1024)
                if not data: break
                clientsocket.sendall(data)


if __name__ == "__main__":    
    host = "localhost"
    port = 50007
    serve(host, port)
