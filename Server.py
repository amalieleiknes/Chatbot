# -*- coding: utf-8 -*-
"""
This needs to run at all times to keep the chatroom running.

    cd Desktop\Skole\Vår2021\Datanettverk og skytjenester\Portfolio1\Chatbot

py Server.py 12345
py Client.py localhost 12345 joan

Problemer:
- jeg kan ikke ha input() funksjonen i samme som "ny tråd", for da
krever den at input skriver flere ganger på rad. Denne må utenfor i egen tråd
og så må den tråden kjøre, og så kan de andre trådene kjøre, og så den igjen.

"""

import _thread
import threading
import socket
import time

addr = 'localhost'
port = 12345  # int(sys.argv[1])

# Create a TCP/IP socket, exactly the same way as in the client
server_socket = socket.socket(type=socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

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
                incoming_data = c.recv(1024)
                incoming_data = incoming_data.decode('utf-8')
                print(incoming_data)

            except:
                c.close()
                connections_list.remove(c)


def receive_from_all():
    for c in connections_list:
        data = c.recv(1024)
        if not data:
            c.close()
        else:
            data = data.decode('utf-8')
            print(data)

            # server forwards msg from client to other clients  after receiving
            #forward_to_rest(c, data)


#  this code is run in parallell for every client
def client_connection_thread(client_conn):
    # sending username to new client as first thing. Only done once.
    client_conn.send(bytes(username.encode('utf-8')))

    while True:
        try:
            # mottar klientsvaret én gang (sendt først fra server input til klient)
            msg = client_conn.recv(1024)
            msg = msg.decode('utf-8')
            print(msg)

            forward_to_rest(client_conn, msg)


        except:
            continue


def server_thread():
    while True:
        # The users input is saved in msg
        time.sleep(2)
        msg = str(input("You: "))

        # user says bye = connection is ended:
        if msg == "bye":
            kill_all_connections()
        else:
            # if not ended, send message to clients
            send_to_all(msg)

            receive_from_all()

            for i in thread_list:
                thread.join()
            time.sleep(2)


thread_list = []

while True:
    server_socket.listen(5)
    # starting with accepting any incoming connections
    client_connection, addr = server_socket.accept()

    if client_connection not in connections_list:
        # appends the list of connections with new conn
        connections_list.append(client_connection)

        # connecting to client and starting new thread for them
        thread = threading.Thread(target=client_connection_thread(client_connection))
        thread_list.append(thread)
        thread.start()

        # starting the server-code
        server_thread()

# printing out on all screens that new client is connected
        print("\nChatbot connected from: ", addr)
        address = ("\nChatbot connected from addr:" + str(addr) + "\n")
        forward_to_rest(client_connection, address)
