import socket
from _thread import *
import sys
from support import read_pos, make_pos

server = '10.55.131.105'
port = 49001

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(s)

s.listen(1)
print('Waiting for a connection, Server Started')

pos = [(0, 0), (100, 100)]
def threaded_client(conn, player):
    conn.send(str.encode(make_pos(pos[player])))
    reply = ''
    while True:
        try:
            data = read_pos(conn.recv(2048).decode())
            pos[player] = data


            if not data:
                print("Disconnected")
                break
            else:
                if player == 1:
                    reply = pos[0]
                else:
                    reply = pos[1]

                print("Recieved: ", data)
                print("Sending : ", reply)

            conn.sendall(str.encode(make_pos(reply)))
        except:
            break

    print("Lost connection")
    conn.close()

currentPlayer = 0
while True:
    conn, addr = s.accept()
    print('Connected to:', addr)

    start_new_thread(threaded_client, (conn, currentPlayer))
    currentPlayer += 1
