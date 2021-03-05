# -*- coding: utf-8 -*-
"""
This needs to run at all times to keep the chatroom running.



py Server.py 12345
py Client.py localhost 12345 joan

Problemer:
- jeg kan ikke ha input() funksjonen i samme som "ny tråd", for da
krever den at input skriver flere ganger på rad. Denne må utenfor i egen tråd
og så må den tråden kjøre, og så kan de andre trådene kjøre, og så den igjen.

"""
#       cd C:\Users\Eier\Desktop\Skole\Vår2021\Datsky\Chatbot


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
server_socket.listen(5)

username = input("Please enter your name: ")

print("Server is running... Wait for a chatbot to join your room")

# making a list of clients, currently with only server_socket as connection
clients_connections_LIST = []
informed_connections_LIST = []


# killing all connections, first the clients and lastly the server
def kill_all_connections():
    for c in clients_connections_LIST:
        if c != server_socket:
            c.close()
    server_socket.close()


# sending the users input msg to all clients connected (except server)
def send_to_all(msg):
    msg = str(username + ":::" + msg)
    msg = msg.encode('utf-8')

    for c in clients_connections_LIST:
        try:
            c.send(bytes(msg))
            informed_connections_LIST.append(c)
        except:
            c.close()
            clients_connections_LIST.remove(c)


# forwarding message received from one client to the rest of the clients through server
def forward_to_rest(conn, msg):
    msg = bytes(msg.encode('utf-8'))

    for c in clients_connections_LIST:
        if c != conn:
            try:
                c.send(msg)
            except:
                c.close()
                clients_connections_LIST.remove(c)


def receive_from_all():
    for c in clients_connections_LIST:
        data = c.recv(1024)
        if not data:
            c.close()
        else:
            data = data.decode('utf-8')
            print(data)

            # server forwards msg from client to other clients  after receiving
            forward_to_rest(c, data)


#  this code is run in parallell for every client
def client_connection_thread(client_conn):
    # sending username to new client as first thing. Only done once.
    client_conn.send(bytes(username.encode('utf-8')))

    while True:
        # Server receives answer from client
        receive_from_all()


def server_thread():
    while True:
        # new_connection()
        try:
            time.sleep(2)
            # The users input is saved in msg
            msg = str(input("You: "))

            # user says bye = connection is ended:
            if msg == "bye":
                kill_all_connections()
            else:
                # if not ended, send message to clients
                send_to_all(msg)


                time.sleep(3)
        except:
            print("?")


_thread.start_new_thread(server_thread, ())


while True:
    # starting with accepting any incoming connections
    client_connection, address = server_socket.accept()

    if client_connection not in clients_connections_LIST:
        # appends the list of connections with new conn
        clients_connections_LIST.append(client_connection)

        # connecting to client and starting new thread for them
        _thread.start_new_thread(client_connection_thread, (client_connection,))

        """
        Problem med å skrive ut at chatbot er connected.
        Vil gjerne ha med dette da det gjør chatten mer responsiv,
        men om jeg ikke finner en løsning er det bedre å kutte det ut
        
        """

        # print("\nChatbot connected from: ", address)
        address = ("\nChatbot connected from addr:" + str(address) + "\n")
        forward_to_rest(client_connection, address)

