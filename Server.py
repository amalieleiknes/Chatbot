# -*- coding: utf-8 -*-
"""
This needs to run at all times to keep the chatroom running.

    cd Desktop\Skole\Vår2021\Datanettverk og skytjenester\Portfolio1\Chatbot

py Server.py 12345
py Client.py localhost 12345 joan

Problemer:
- Klientenes meldinger kommer litt hytt i pine på server og klient
- når en ny klient logger på kommer "logget på m adr" etter "you"
- hvordan kan jeg få "accept new conn" til å vente til alle meld er received
    før den leter etter nye conn?
    Vil gjerne da få inn ny conn rett før "you: " kommer opp i terminalen

    tror problemet er at den receiver og så sender videre, og da sender den gjerne
    tilbake det som er blitt forwardet og da kommer ting flere ganger.
    Bør kanskje lage en liste med innkommende meldinger fra klient til server
    med tilhørende connectionnummer og så sende denne til alle connections som den ikke
    kommer fra ellerno?

"""

import _thread
import threading
import socket
import time

addr = 'localhost'
port = 12345  # int(sys.argv[1])

# Create a TCP/IP socket, exactly the same way as in the client
server_socket = socket.socket(type=socket.SOCK_STREAM)

# bind means to reserve a local socket. Server will also be listening for answers
server_socket.bind((addr, port))

username = input("Please enter your name: ")

print("Server is running... Wait for a chatbot to join your room")

# making a list of clients, currently with only server_socket as connection
connections_list = []


# killing all connections, first the clients and lastly the server
def kill_all_connections():
    for c in connections_list:
        if c != server_socket:
            c.close()
    server_socket.close()


# sending the users input msg to all clients connected (except server)
def send_to_all(msg):
    msg = str(username + ":::" + msg)
    msg = msg.encode('utf-8')

    for c in connections_list:
        try:
            c.send(bytes(msg))
        except:
            c.close()
            connections_list.remove(c)


# forwarding message received from one client to the rest of the clients through server
def forward_to_rest(conn, msg):
    msg = bytes(msg.encode('utf-8'))

    for c in connections_list:
        if c != conn:
            try:
                c.send(msg)
            except:
                c.close()
                connections_list.remove(c)


def receive_from_all(conn):
    for c in connections_list:
        if c != conn:
            data = c.recv(1024)
            if not data:
                conn.close()
            else:
                data = data.decode('utf-8')
                print(data)


"""
:
    1. først sendes brukernavnet over til client.py for hver tråd
    2. så mottar hver tråd fra client.py et svar fra en bot
    3. så kan det printes ut her på serveren
    4. så kan hver tråd sende hvert sitt svar over til de andre trådene
        a. en og en tråd sender over til de andre trådene.
    5. så mottar hver tråd fra de andre trådene
"""
#  this code is run in parallell for every client
def client_connection_thread(client_conn):
    # sending username to new client as first thing. Only done once.
    client_conn.send(bytes(username.encode('utf-8')))

    while True:
        try:
            # receiving data from server (userinput)
            data = server_socket.recv(1024)

            # Server receives answer from client
            receive_from_all(client_conn)

        except:
            continue


server_socket.listen(5)


"""
Her skal serveren kjøre:
 1. starter med å hente input fra bruker
 2. fortsetter med å sjekke om det er "bye"
 3. sender melding til alle andre connections/ tråder
 4. motta svar fra alle connections og printer det ut
 5. ber sin egen tråd om å vente til de andre trådene har mottatt alt
"""
def server_connection_thread():
    time.sleep(2)
    msg = str(input("You: "))

    # user says bye = connection is ended:
    if msg == "bye":
        kill_all_connections()
    else:
        # if not ended, send message to clients
        send_to_all(msg)

        receive_from_all()

     # waiting until all other threads are done


while True:
    # starting with accepting any incoming connections
    client_connection, addr = server_socket.accept()

    if client_connection not in connections_list:

        # appends the list of connections with new conn
        connections_list.append(client_connection)

        # connecting to client and starting new thread for them
        _thread.start_new_thread(client_connection_thread, (client_connection,))

        print("\nChatbot connected from: ", addr)
        address = ("\nChatbot connected from addr:" + str(addr) + "\n")
        forward_to_rest(client_connection, address)
