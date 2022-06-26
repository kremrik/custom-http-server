import socket
from socket import AF_INET, SOCK_STREAM
from time import sleep


def connect(
    message, 
    host="localhost", 
    port=50007, 
    buff_size=8
):
    with socket.socket(AF_INET, SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(message)

        response = b""
        while True:
            data = s.recv(buff_size)
            response += data
            if len(data) < buff_size:
                break

        print(response.decode())
        sleep(10)
        s.shutdown(1)


if __name__ == "__main__":
    message = b"GET /path/to/resource HTTP/1.1\nHost: localhost\nAccept-Language: en\n\nTHIS IS SOME BODY TEXT"
    connect(message)
