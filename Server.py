# -*- coding: utf-8 -*-
"""
This needs to run at all times to keep the chatroom running.

To exit the chat and end all connections, input "bye".

"""
#       cd C:\Users\Eier\Desktop\Skole\Vår2021\Datsky\Chatbot

import _thread
import time
import sys
import socket

addr = 'localhost'
port = int(sys.argv[1])

# Create a TCP/IP socket, exactly the same way as in the client
server_socket = socket.socket(type=socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

# bind means to reserve a local socket. Server will also be listening for answers
server_socket.bind((addr, port))
server_socket.listen(4)

username = input("\nPlease enter your name: ")
print("")

print("Welcome to the chat! Please wait for a chatbot to connect before asking questions.")

# making a list of clients, currently with only server_socket as connection
clients_connections_LIST = []
clients_names_LIST = []
new_connection = []


class bots:
    def __init__(self, botname, connection):
        self.botname = botname
        self.connection = connection


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

        # receiving botname, adding it to list with connections
        name = client_conn.recv(1024)
        clients_names_LIST.append(bots(name, client_conn))

        while True:
            # Server receives answer from client
            receive_from_all()
    except:
        print("\nNo chatbots connected, please wait for a new connection.\n")


def check_for_new_connections():
    # printing the new connection and then removing from list
    # printing out new connection at the other clients
    name = update_botconnections(client_connection)
    print("\nNew chatbot connected from: " + str(address) +
          ", say hello to " + str(name) + "!\n")
    new_connection.clear()


def update_botconnections(client_conn):
    # checking whether the connection is still alive or not
    for i in clients_names_LIST:
        if i.connection not in clients_connections_LIST:
            clients_names_LIST.remove(i)

        # finding the botname to the given connection
        if i.connection == client_conn:
            return i.botname


def server_thread():
    while 1:
        i = 0
        if len(clients_connections_LIST) > 0:
            i = 0
            try:
                if len(new_connection) > 0:
                    check_for_new_connections()

                # printing out a new line to have a nicer output in terminal
                print("")

                # The users input on server is saved in msg
                msg = str(input("You: "))

                # user says bye in terminal -> connection is ended.
                if msg == "bye":
                    kill_all_connections()
                else:

                    if len(new_connection) > 0:
                        check_for_new_connections()
                        time.sleep(1)

                    # if not ended, send message to all clients
                    send_to_all(msg)

                    # wait for all bots to send their message back to server
                    time.sleep(3)

            except:
                print("Exception: Failure in server-thread.")
        else:
            print("Please wait for a chatbot to connect ...")
            time.sleep(5)
            i += 1
            if i == 10:
                server_socket.close()


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
        bn = update_botconnections(client_connection)
        address = ("\nNew chatbot connected from: " + str(address) +
                   ", say hello to \n" + str(bn) + "!")
        forward_to_rest(client_connection, address)
