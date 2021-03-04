# -*- coding: utf-8 -*-
"""
The client.py is meant to implement the different chatbots.
When someone connects to the server, one or more chatbots can connect via the client,
where different chatbots will answer questions from input on server.

You can choose between the following chatbots:
    1. Joan (a nice person)
    2. Joker (loves to tell jokes)
    3. Jake (sad guy)
    4. Jimmy ()
    5. Java ()
"""

import socket
import time
import sys
import random

addr = str(sys.argv[1])
port = int(sys.argv[2])
bot = sys.argv[3]
bot = bot.lower()

client_socket = socket.socket(type=socket.SOCK_STREAM)
client_socket.connect((addr, port))

# making a list of different bots
bots_list = ["joan", "joker", "jake", "jimmy", "java"]

print("Client is running ...\t", addr, ":", port, "\t Botname:", bot)


# Joan is a simple chatbot who cannot do so much
def joan(action, greeting):
    string = ""
    if greeting != "":
        string = greeting

    if action == "":
        string += "?"
    else:
        string += "Ooo I would love to go for a " + action

    return string


# Joker is the chatbot-clown who can do a bit more than Joan
def joker(joke):
    if joke == "knock":
        string = "Knock Knock"
    elif joke == "who's there" or joke == "who is there":
        string = "Cows go"
    elif joke == "cows go who":
        string = "Cows go moo!"
    elif joke == "cows go moo":
        string = "You ruined my joke:("
    elif joke == "children":
        string = "All the children were planned, except Jake. His parents made a mistake."
    else:
        string = "I don't know anymore jokes"
    return string


def jake(action, joke):
    if joke == "cows go":
        string = "Cows go moo"
    else:
        string = "I'm Jake"
    return string


def jimmy(action):
    string = "hi there"
    return string


def java(action, greeting, joke):
    string = "hello i don't like python"
    return string


def bots_all(action, greeting, joke):
    if bot == "joan":
        string = joan(action, greeting)

    elif bot == "joker":
        string = joker(joke)

    elif bot == "jake":
        string = jake(action, joke)

    elif bot == "jimmy":
        string = jimmy(action)

    elif bot == "java":
        string = java(action, greeting, joke)

    else:
        string = "No bots have entered name. Must fix with input at beginning of client"
        # if none of these bots are chosen,
        # there will be a null response and the client is ended

    return string


def analyze(userinput):
    userinput = userinput.lower()

    action = ""
    joke = ""
    greeting = ""

    greetings_input = ["hi", "hello", "hey"]
    greetings_response = ["howdy ", "Hi there fellow humanbeing! ", "holla! ", "what's up", "So nice to finally meet a cool person" , "*nods*"]

    # making a list of actions that chatbots understand
    actions_input = ["annoy", "build", "create", "drive", "explore", "find", "help", "jog"]
    actions_suggestions = []

    # making a list of jokes
    jokes = ["knock knock", "cows go who", "cows go moo", "who's there", "who is there" "all the children"]

    # finding if there is a greeting
    for g in greetings_input:
        if g in userinput:
            greeting = random.choice(greetings_response)
            break

    # finding the verb for what the user wants to do
    for a in actions_input:
        if a in userinput:
            time.sleep(1)
            action = a
            break

    # looking for jokes
    for j in jokes:
        if j in userinput:
            joke = j
            break

    # finding response from bot present
    string = bots_all(action, greeting, joke)

    # returning suggested action and bots name        
    return string


# receiving the username so that we know who needs answers
username = client_socket.recv(1024)
username = username.decode('utf-8')

# in a loop as long as server(user) is online/ until they say bye
while True:
    new_connection_info = "Chatbot connected from addr:"

    # data saves what the user is asking about
    data = client_socket.recv(1024)
    data = data.decode('utf-8')

    if not data:
        client_socket.close()

    # if connection is
    elif new_connection_info in data:
        print(data)

    else:

        # if trying fails, it means it is not from userinput
        try:
            # making a list over who sent the msg + contents of msg
            name_and_msg_list = data.split(':::')
            name = name_and_msg_list[0]
            msg = name_and_msg_list[1]

            # if the user sent the message, we want the bot to respond
            if name == username:
                print(name + ": " + msg)

                response = analyze(msg)
                time.sleep(1)
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

