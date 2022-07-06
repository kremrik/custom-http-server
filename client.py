import socket
from socket import AF_INET, SOCK_STREAM
from sys import argv
from time import sleep


def connect(
    message,
    sleep_for,
    host="localhost", 
    port=8080, 
    buff_size=8
):
    with socket.socket(AF_INET, SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(message)
        
        sleep(sleep_for)

        response = b""
        while True:
            data = s.recv(buff_size)
            response += data
            if len(data) < buff_size:
                break

        print(response.decode())
        s.shutdown(1)


if __name__ == "__main__":
    sleep_for = int(argv[1])
    message = b"GET /path/to/resource HTTP/1.1\nHost: localhost\nAccept-Language: en\n\nTHIS IS SOME BODY TEXT"
    connect(message, sleep_for)
