# -*- coding: utf-8 -*-
"""
Client.py is meant to implement the different chatbots.
When a user connects to the server, one or more clients (chatbots) can connect.
The chatbots reacts to the user input on server.

The following chatbots can be chosen:
    1. Joan (a nice bot)
    2. Joker (loves to tell jokes)
    3. Jake (hates joker's jokes)
    4. Jimmy (an unhappy bot)
"""

import socket
import sys
import random
import time

if len(sys.argv) != 4:
    print("Please put in the following arguments:\n"
          "py [application] [address to connect to] [port to connect to] [bot to connect to]")

else:
    addr = str(sys.argv[1])
    port = sys.argv[2]
    bot = str(sys.argv[3]).lower()

    try:
        port = int(port)
    except ValueError:
        print("Portnumber is not valid. Try for example 12345")

    # making a list of different bots
    bots_list = ["joan", "joker", "jake", "jimmy"]

    if port is None or addr == "":
        print("Not valid address or port")

    # only connecting if the bot inputted is available
    elif bot not in bots_list:
        print("Bot named is not available. Please try with one of the following botnames:")
        for i in bots_list:
            print(i)

    # telling the client which bots are available for connecting
    else:
        client_socket = socket.socket(type=socket.SOCK_STREAM)

        # if server does not send any messages in 60 secs, client logs off
        client_socket.settimeout(60)
        client_socket.connect((addr, port))
        print("Client is running ...\t", addr, ":", port, "\t Botname:", bot)

        # receiving the users name from server
        username = client_socket.recv(1024)
        username = username.decode('utf-8')

        # sending the bots name to server
        botname = bot.encode('utf-8')
        client_socket.send(bytes(botname))


        def joan(action, greeting, goodbye):
            string = ""
            greetings_response = ["howdy ... ", "Hi there fellow humanbeing! ", "holla! ",
                                  "what's up !? ", "So nice to finally meet a cool person. ",
                                  "*nods* ", "Can I help you with anything? "]

            if action == "" and greeting == "":
                string = "What? "

            if greeting != "":
                string = random.choice(greetings_response)

            if action == "joke":
                string = "I don't know any jokes, sorry. But Joker knows 'em all."

            elif action != "":
                string += "Ooo I would love to go for a " + action + " :D"

            if goodbye != "":
                string += "I am not leaving :("

            time.sleep(1)

            return string


        def joker(action):
            jokes_list = ["All the children were planned, except Jake. His parents made a mistake ;)",
                          "All the children got to have cake, except Jake. His mother forgot to bake ;)",
                          "I don't know anymore jokes :("]

            if action == "joke":
                string = random.choice(jokes_list)
                print("[Haha, I am so funny]")

            else:
                string = "I don't want to talk about anything else but jokes. "

            return string


        def jake(action, bad_act):
            random_strings = ["I'm Jake", "I am Jake", "You are not Jake", "Jake is my favorite word"]
            string = random.choice(random_strings)

            if action == "joke":
                string = "Please don't ask Joker to tell a joke, he is so mean to me :("
                print("[I need to find som jokes about Joker ASAP]")

            if bad_act != "":
                string = bad_act + " you say?? I would love to do that to Joker."

            return string


        def jimmy(action):
            if action != "":
                string = "Let's not do some " + action + "ing, please. "
            else:
                string = "Don't you know what you wanna do? "
                print("[Ugh, why can't this person just decide???]")

            actions_suggestions = ["answer", "break", "clean", "doodle", "bake"]
            suggestions = random.choice(actions_suggestions)

            string += "Could we rather " + str(suggestions) + "?"
            return string


        def bots_all(action, greeting, bad_act, goodbye):
            string = ""

            if bot == "joan":
                string = joan(action, greeting, goodbye)

            elif bot == "joker":
                string = joker(action)

            elif bot == "jake":
                string = jake(action, bad_act)

            elif bot == "jimmy":
                string = jimmy(action)

            return string


        def analyze(userinput):
            userinput = userinput.lower()

            action = ""
            greeting = ""
            bad_action = ""
            goodbye = ""

            # array of goodbyes
            gb = ["bye", "goodbye", "see you soon"]

            greetings_input = ["hi", "hello", "hey", "what\'s up", "how are you",
                               "good morning", "good evening", "good afternoon"]

            # making a list of actions that chatbots understand
            actions_input = ["sing", "ask", "create", "drive", "explore", "find", "help",
                             "jog", "walk", "work", "call", "make", "use", "joke"]

            bad_actions_input = ["hate", "kill", "spit", "break", "sabotage"]

            if "bye" in userinput:
                goodbye = random.choice(gb)

            # finding if there is a greeting
            for g in greetings_input:
                if g in userinput:
                    greeting = g
                    break

            # finding if the user asks about a nice action
            for a in actions_input:
                if a in userinput:
                    action = a
                    break

            # finding if the user asks about a bad action
            for a in bad_actions_input:
                if a in userinput:
                    bad_action = a
                    break

            # finding response from bot connected
            string = bots_all(action, greeting, bad_action, goodbye)

            # returning suggested action
            return string


        # in a loop as long as server(user) is online/ until they say bye
        while True:
            # string equal to what is printed when a new client connects
            new_connection_info = "chatbot connected from:"

            # data saves what the user is asking about
            data = client_socket.recv(1024)
            data = data.decode('utf-8')

            # if there is no data from server, the connection should be closed
            if not data:
                client_socket.close()

            # if received data is info about a new connection, do not analyze it - only print
            elif new_connection_info in data:
                print(data)

            else:
                # if trying fails, it means it is not from user input but from bot
                try:
                    # making a list over who sent the msg + contents of msg
                    name_and_msg_list = data.split(':::')
                    name = name_and_msg_list[0]
                    msg = name_and_msg_list[1]

                    # if the user sent the message, we want the bot to respond
                    if name == username:
                        print(name + ": " + msg)

                        # if user said goodbye to the chatbot, we end the connection
                        if "bye" in msg and str(bot) in msg:
                            print("OMG was I just kicked out???")
                            time.sleep(1)
                            client_socket.close()

                        else:
                            response = analyze(msg)
                            print("You: " + response)

                            # formatting response so botname is attached, then encoding it
                            response = bot + ": " + response
                            response = response.encode('utf-8')

                            # sending response back to server
                            client_socket.send(response)
                except:
                    print(data)
