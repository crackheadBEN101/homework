import random
import json
import csv
import os
import getpass
import time
import sys
from turtle import title

from termcolor import colored, cprint
from getpass import getpass
from reprint import output

user_data = {}
song_data = []
user_score = {}
username = ""

DATA_FILE = "data.json"
SONG_FILE = "song.csv"

def clrscr():
   if os.name == 'posix':
      _ = os.system('clear')
   else:
      _ = os.system('cls')

def save_data():
    global user_data
    f = open(DATA_FILE, "w")
    f.write(json.dumps(user_data))
    f.close()

#Check if files exist
if os.path.isfile(DATA_FILE):
    #Open data.json file
    f = open(DATA_FILE, "r")
    #Loads the file as json and as user_data
    user_data = json.loads(f.read())
    #Close the file
    f.close()

#Check if files exist
if os.path.isfile(SONG_FILE):
    with open(SONG_FILE,'r') as songlist:
            csv_source  = csv.DictReader(songlist)
            song_data = list(csv_source)

def login():
    global user_data
    global username
    clrscr()
    print("Welcome to the Music Quiz Game")
    print("Created by BEN101")
    print("")
    print("Please login to continue.")
    print("Username:")
    username = input("> ")
    print("Password:")
    password = getpass("(Hidden)> ")

    #Check identity
    try:
        if user_data[username]["password"] == password:
            #Pass, clear screen
            cprint("Login Success! Welcome back, %s"%username, "green")
            time.sleep(0.5)
            menu()
        else:
            #Wrong password
            cprint("Login Unsuccessful! Please check your credentials!", "red")
            time.sleep(1)
            login()
    except KeyError:
        #Missing username in JSON
        cprint("Login Unsuccessful! Unknown username, Please check your credentials!", "red")
        time.sleep(1)
        login()

def menu():
    clrscr()
    save_data()
    print("")
    print("Menu")
    print("--------------------")
    print("1. Play!")
    print("2. Settings")
    print("")
    print("9. Quit")
    print("")
    print("Please select by number:")
    selection = input("> ")
    if selection == "1":
        game()
    elif selection == "2":
        #settings()
        #not ready, ready remove "pass"
        pass
    elif selection == "9":
        sys.exit()
    else:
        cprint("Invalid Input!", "red")
        time.sleep(1)
        menu()

def game():
    global user_data
    global song_data
    clrscr()
    print("Welcome to the music game")
    print("--------------------")
    print("\n")
    
    chosen_one = random.choice(song_data)
    songs_word = chosen_one["Song"].split()
    song_first = "".join(item[0] for item in songs_word)
    first_uppercase = song_first.upper()
    print("here 's an artist: " + chosen_one["Artists"])
    print("This is the first word of the song: " + first_uppercase)
    print("What is the name of the song:")
    user_guess = input("> ")
    if chosen_one["Song"].upper() == user_guess.upper():
        print("Well done, You get Two points.")
        
        #This check if "score" exist in user_data[username]
        if "score" in user_data[username]:
            #If yes, meaning player already have a score, add 2 on top of it
            user_data[username]["score"] = user_data[username]["score"] + 2
        else:
            #If no, meaing player doesn't have a score, set the score to 2
            user_data[username]["score"] = 2

        time.sleep(1)
        clrscr()
        print("Want to play again? Yes/No ")
        play_again = input("> ")
        if play_again == "Yes" or play_again == "yes":
            clrscr()
            game()
        else:
            menu()
    else:
        print("Sorry, Wrong answer. You have one more chance to guess it")
        print("What is the name of the song:")
        user_guess = input("> ")
        if chosen_one["Song"].upper() == user_guess.upper():
            print("Well done, You get One point.")
            time.sleep(1)
            clrscr()
            print("Want to play again? Yes/No ")
            play_again = input("> ")
            if play_again == "Yes" or play_again == "yes":
                clrscr()
                game()
            else:
                menu()
        else:
            print("Game Over")
            time.sleep(1)
            menu()
login()
