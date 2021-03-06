# -*- coding: utf-8 -*-
"""
This needs to run at all times to keep the chatroom running.

To exit the chat and end all connections, input "bye".

"""
#       cd C:\Users\Eier\Desktop\Skole\Vår2021\Datsky\Chatbot

import _thread
import socket
import time
import sys

addr = 'localhost'
port = int(sys.argv[1])

# Create a TCP/IP socket, exactly the same way as in the client
server_socket = socket.socket(type=socket.SOCK_STREAM)

# bind means to reserve a local socket. Server will also be listening for answers
server_socket.bind((addr, port))
server_socket.listen(5)

username = input("\nPlease enter your name: ")
print("")

print("Welcome to the chat! Please wait for a chatbot to connect before asking questions.")

# making a list of clients, currently with only server_socket as connection
clients_connections_LIST = []
new_connection = []


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
        try:
            data = c.recv(1024)
            if not data:
                c.close()
            else:
                data = data.decode('utf-8')
                print(data)

                # server forwards msg from client to other clients  after receiving
                forward_to_rest(c, data)
        except:
            c.close()
            clients_connections_LIST.remove(c)


#  this code is run in parallell for every client
def client_connection_thread(client_conn):
    try:
        # sending username to new client as first thing. Only done once.
        client_conn.send(bytes(username.encode('utf-8')))

        while True:
            # Server receives answer from client
            receive_from_all()
    except:
        print("\nNo chatbots connected, please wait for a new connection.\n")


def check_for_new_connections():
    # printing the new connection and then removing from list
    print("\nNew chatbot connected from: " + str(new_connection[0]) + "\n")
    new_connection.clear()


def server_thread():
    while True:
        if len(clients_connections_LIST) > 0:
            try:
                if len(new_connection) > 0:
                    check_for_new_connections()
                    # The users input is saved in msg
                    msg = str(input("You: "))

                    # user says bye = connection is ended:
                    if msg == "bye":
                        kill_all_connections()
                    else:

                        if len(new_connection) > 0:
                            check_for_new_connections()
                            time.sleep(1)

                        # if not ended, send message to clients
                        send_to_all(msg)

                        # wait for all bots to send their message and think
                        time.sleep(4)

            except:
                print("Exception: Failure in server-thread.")
                server_socket.close()

        # bør ha med en tidsbegrensning - hvis ikke nye chatbots joiner vil serveren lukkes?
        else:
            server_socket.close()
            continue

_thread.start_new_thread(server_thread, ())

while True:
    # starting with accepting any incoming connections
    client_connection, address = server_socket.accept()

    if client_connection not in clients_connections_LIST:
        # appends the list of connections with new conn
        clients_connections_LIST.append(client_connection)

        # connecting to client and starting new thread for them
        _thread.start_new_thread(client_connection_thread, (client_connection,))

        # adding the new connection to list so that server can print out separately
        new_connection.append(address)

        # printing out new connection at the other clients
        address = ("\nNew chatbot connected from: " + str(address) + "\n")
        forward_to_rest(client_connection, address)
