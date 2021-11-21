import socket, errno
import random


def getPort():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    port = random.randint(1111,9999)
    try:
        s.connect(("127.0.0.1",port))
    except socket.error as e:
        if e.errno == errno.EADDRINUSE:
            print('port not free')
        else:
            print(e)

    s.close()
    return port

if __name__ == '__main__':
    print(getPort())