# -*- coding: utf-8 -*-
"""
A short explanation of functions:
This needs to run at all times to keep the chatroom running.
To exit the chat and end all connections, input "bye".
To end only one connection, type "bye [botname]"
"""
#       cd C:\Users\Eier\Desktop\Skole\Vår2021\Datsky\Chatbot
#       py Client.py localhost 12345 joan

import _thread
import time
import sys
import socket

if len(sys.argv) != 2:
    print("Please put in the following arguments:\n"
          "py [application] [port to connect to]")

else:
    addr = 'localhost'
    port = sys.argv[1]

    try:
        port = int(port)
    except ValueError:
        print("Portnumber is not valid. Try for example 12345")

    if port == "":
        print("Please type a valid port to connect")

    else:
        # Create a TCP/IP socket, exactly the same way as in the client
        server_socket = socket.socket(type=socket.SOCK_STREAM)

        # enables the reuse of addresses
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # bind means to reserve a local socket. Server will also be listening for answers
        server_socket.bind((addr, port))
        server_socket.listen(4)

        username = input("\nPlease enter your name: ")

        # if username is invalid, you have to start over
        if ":" in username:
            print("Invalid username. Cannot have a colon in your username.")
            server_socket.close()
        elif username == "":
            print("Invalid username. Cannot have an empty username.")
            server_socket.close()

        # username OK, continue
        else:
            print("")

            print("Welcome to the chat! Please wait for a chatbot to connect before asking questions. \n"
                  "The chatbot will log off if you use more than 40 seconds to type a message.")

            # making a list of clients, currently with only server_socket as connection
            clients_connections_LIST = []
            clients_names_LIST = []
            new_connections_LIST = []
            disconnected_LIST = []

            # making a class to be able to make a list of bot-objects
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
                    except socket.error:
                        disconnected_LIST.append(c)
                        c.close()
                        try:
                            clients_connections_LIST.remove(c)
                        except:
                            print("")

            # forwarding message received from one client to the rest of the clients through server
            def forward_to_rest(conn, msg):
                msg = bytes(msg.encode('utf-8'))

                for c in clients_connections_LIST:
                    if c != conn:
                        try:
                            c.send(msg)
                        except socket.error:
                            disconnected_LIST.append(c)
                            c.close()
                            try:
                                clients_connections_LIST.remove(c)
                            except:
                                print("")

            # receiving message from all the other clients
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
                    except socket.error:
                        disconnected_LIST.append(c)
                        c.close()
                        try:
                            clients_connections_LIST.remove(c)
                        except:
                            print("")

            #  this code is run in parallel for every client
            def client_connection_thread(client_conn):
                try:
                    # sending username to new client as first thing. Only done once.
                    client_conn.send(bytes(username.encode('utf-8')))

                    # receiving botname, adding it to list with connections
                    name = client_conn.recv(1024)
                    name = name.decode('utf-8')
                    clients_names_LIST.append(bots(name, client_conn))

                    while True:
                        # Server receives answer from client
                        receive_from_all()
                except socket.error:
                    time.sleep(1)
                    print("\nNo chatbots connected, please wait for a new connection.\n")

            # checking if there has been any new connections since last time checked
            def check_for_new_connections():
                # updating names and conn list
                update_bot_connections()

                # finding the botname to the given connection
                for j in new_connections_LIST:
                    for i in clients_names_LIST:
                        if j == i.connection:
                            print("\nNew chatbot connected, say hello to " + str(i.botname) + "!\n")
                new_connections_LIST.clear()

            # checking if any connections got disconnected while chatting
            def check_disconnected_clients(dl):
                dl = list(set(dl))
                for i in clients_names_LIST:
                    for j in dl:
                        if i.connection == j:
                            print(i.botname, "just disconnected :(")
                disconnected_LIST.clear()

            # updating the list of bot-connections and returning botname of given connection
            def update_bot_connections():
                # checking whether the connection is still alive or not
                for i in clients_names_LIST:
                    if i.connection not in clients_connections_LIST:
                        try:
                            clients_names_LIST.remove(i)
                        except:
                            print("Failed to update conn_LIST)")

            def kill_bot_connection(m):
                for i in clients_names_LIST:
                    if i.botname in m:
                        clients_connections_LIST.remove(i.connection)

            # thread for the server input and sending of info to clients
            def server_thread():
                i = 0
                while 1:
                    if len(clients_connections_LIST) > 0:
                        try:
                            # checking for new and disconnected clients
                            if len(new_connections_LIST) > 0:
                                check_for_new_connections()
                            if len(disconnected_LIST) > 0:
                                check_disconnected_clients(disconnected_LIST)

                            # The users input on server is saved in msg
                            msg = str(input("You: "))

                            # user says bye in terminal -> connection is ended.
                            if msg == "bye":
                                kill_all_connections()

                            else:
                                # checking for new and disconnected clients again
                                if len(new_connections_LIST) > 0:
                                    check_for_new_connections()
                                if len(disconnected_LIST) > 0:
                                    check_disconnected_clients(disconnected_LIST)

                                # if not ended, send message to all clients
                                send_to_all(msg)

                                # if user says bye to a specific bot
                                if "bye" in msg:
                                    kill_bot_connection(msg)

                                # wait for all bots to send their message back to server
                                time.sleep(2)

                            # setting i to 0 so timeout is reset
                            i = 0
                        except:
                            print("Exception: Failure in server-thread.")
                            server_socket.close()
                    else:
                        if len(disconnected_LIST) > 0:
                            check_disconnected_clients(disconnected_LIST)

                        # If no chatbots are connected, give user a message about this.
                        if i == 1:
                            print("Please wait for a chatbot to connect ...")
                        time.sleep(5)
                        i += 1

                        # If no chatbot connects in the next 30secs, close server socket.
                        if i == 8:
                            print("Sorry, no chatbots available. Please try again later.")
                            server_socket.close()


            # starting a thread for the server
            _thread.start_new_thread(server_thread, ())

            # always looking for new connections from clients
            while True:
                # starting with accepting any incoming connections
                client_connection, address = server_socket.accept()

                if client_connection not in clients_connections_LIST:
                    # appends the list of connections with new conn
                    clients_connections_LIST.append(client_connection)

                    # connecting to client and starting new thread for them
                    _thread.start_new_thread(client_connection_thread, (client_connection,))

                    # adding the new connection to list so that server can print out separately
                    new_connections_LIST.append(client_connection)

                    # informing other clients about new connection
                    info = ("\nAnother chatbot connected from: " + str(address) +
                            ".\n")
                    forward_to_rest(client_connection, info)
