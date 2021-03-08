# -*- coding: utf-8 -*-
"""
The client.py is meant to implement the different chatbots.
When someone connects to the server, one or more chatbots can connect via the client,
where different chatbots will answer questions from input on server.

You can choose between the following chatbots:
    1. Joan (a nice person)
    2. Joker (loves to tell jokes)
    3. Jake (hates joker's jokes)
    4. Jimmy ()

No bots have entered name. Must fix with input at beginning of client??
Must ensure one of these five names have been entered

"""

import socket
import sys
import random
import time

addr = str(sys.argv[1])
port = int(sys.argv[2])
bot = sys.argv[3]
bot = bot.lower()

# making a list of different bots
bots_list = ["joan", "joker", "jake", "jimmy"]

# only connecting if the bot inputted is available
if bot not in bots_list:
    print("Bot named is not available. Please try with one of the following botnames:")
    for i in bots_list:
        print(i)

# telling the client which bots are available for connecting
else:
    client_socket = socket.socket(type=socket.SOCK_STREAM)
    client_socket.connect((addr, port))
    print("Client is running ...\t", addr, ":", port, "\t Botname:", bot)

    # receiving the users name from server
    username = client_socket.recv(1024)
    username = username.decode('utf-8')

    # sending the bots name to server



    def joan(action, greeting):
        string = ""
        greetings_response = ["howdy ", "Hi there fellow humanbeing! ", "holla! ",
                              "what's up", "So nice to finally meet a cool person",
                              "*nods*", "Can I help you with anything?"]

        if action == "" and greeting == "":
            string = "What?"

        if greeting != "":
            string = random.choice(greetings_response)

        if action == "joke":
            string = "I don't know any jokes, sorry. But Joker knows 'em all."

        elif action != "":
            time.sleep(1)
            string += "Ooo I would love to go for a " + action

        return string


    def joker(action):
        jokes_list = ["All the children were planned, except Jake. His parents made a mistake.",
                      "All the children got to have cake, except Jake. His mother forgot to bake.",
                      "I don't know anymore jokes"]

        if action == "joke":
            string = random.choice(jokes_list)

        else:
            string = "I don't want to talk about anything else but jokes. " \
                     "So just ask me to tell a joke"

        return string


    def jake(action):
        random_strings = ["I'm Jake", "I am Jake", "You are not Jake", "Jake is my favorite word"]
        string = random.choice(random_strings)

        if action == "joke":
            string = "Please don't ask Joker to tell a joke, he is so mean to me :("
        return string


    def jimmy(action):
        if action != "":
            string = "Let's not do some " + action + "ing, please. "
        else:
            string = "Don't you know what you wanna do? "

        actions_suggestions = ["answer", "break", "clean", "doodle", "bake"]
        suggestions = random.choice(actions_suggestions)

        string += "Could we rather " + str(suggestions) + "?"

        return string


    def bots_all(action, greeting):
        string = ""

        if bot == "joan":
            string = joan(action, greeting)

        elif bot == "joker":
            string = joker(action)

        elif bot == "jake":
            string = jake(action)

        elif bot == "jimmy":
            string = jimmy(action)

        return string


    def analyze(userinput):
        userinput = userinput.lower()

        action = ""
        greeting = ""

        greetings_input = ["hi", "hello", "hey", "what\'s up", "how are you"]

        # making a list of actions that chatbots understand
        actions_input = ["tell", "ask", "create", "drive", "explore", "find", "help",
                         "jog", "walk", "work", "call", "make", "use", "joke"]

        # finding if there is a greeting
        for g in greetings_input:
            if g in userinput:
                greeting = g
                break

        # finding the verb for what the user wants to do
        for a in actions_input:
            if a in userinput:
                action = a
                break

        # finding response from bot present
        string = bots_all(action, greeting)

        # returning suggested action and bots name
        return string


    # in a loop as long as server(user) is online/ until they say bye
    while True:
        # string equal to what is printed when a new client connects
        new_connection_info = "New chatbot connected from: "

        # data saves what the user is asking about
        data = client_socket.recv(1024)
        data = data.decode('utf-8')

        if not data:
            client_socket.close()

        # if connection is
        elif new_connection_info in data:
            print(data)

        else:
            # if trying fails, it means it is not from user input
            try:
                # making a list over who sent the msg + contents of msg
                name_and_msg_list = data.split(':::')
                name = name_and_msg_list[0]
                msg = name_and_msg_list[1]

                # if the user sent the message, we want the bot to respond
                if name == username:
                    print(name + ": " + msg)

                    response = analyze(msg)
                    print("You: " + response)

                    # formatting response so botname is attached, then encoding it
                    response = bot + ": " + response
                    response = response.encode('utf-8')

                    # sending response back to server
                    client_socket.send(response)
            except:
                check_bot_name = data.split(':')
                if check_bot_name[0] != bot:
                    print(data)
