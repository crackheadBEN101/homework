#Import libraries
import os
import sys

import time
import json
import random

from termcolor import colored, cprint
from getpass import getpass
from urllib.parse import urlparse, parse_qs

from reprint import output
import httpx
import youtube_dl
import vlc

#Constant Variable
DATA_FILE = "data.json"
SONG_FILE = "song.json"
SONG_FOLDER = "songs/"
YOUTUBE_API_KEY = "AIzaSyAjvmQBRkXpAPqrzgJovG5Zsr1YA36wDU8"

#ENV Variable
user_data = {}
song_data = []
username = ""

#Basic Functions
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

def save_song():
    global song_data
    f = open(SONG_FILE, "w")
    f.write(json.dumps(song_data))
    f.close()

def containsNumber(value):
    for character in value:
        if character.isdigit():
            return True
    return False

#Check if files exist
if os.path.isfile(DATA_FILE):
    #Open data.json file
    f = open(DATA_FILE, "r")
    #Loads the file as json and as user_data
    user_data = json.loads(f.read())
    #Close the file
    f.close()

if os.path.isfile(SONG_FILE):
    f = open(SONG_FILE, "r")
    song_data = json.loads(f.read())
    f.close()


def settings_resetpw():
    global user_data
    global username
    clrscr()
    print("")
    print("Reset Password")
    print("--------------------")
    print("")
    print("Please enter your new password:")
    newpw = getpass("(Hidden)> ")
    print("Please enter your new password again:")
    confirmpw = getpass("(Hidden)> ")
    if newpw == confirmpw:
        user_data[username]["password"] = newpw
        cprint("Password Reset Succesful!", "green")
        time.sleep(0.3)
        save_data()
        settings()
    else:
        cprint("Password entered is not the same!", "red")
        time.sleep(1)
        settings()

def settings_adduser():
    global user_data
    clrscr()
    print("")
    print("Add New User")
    print("--------------------")
    print("")
    print("Please enter new user name:")
    addusername = input("> ")
    if addusername in user_data:
        cprint("Username Taken!", "red")
        time.sleep(1)
        settings()
    print("Please enter new user password:")
    adduserpw = getpass("(Hidden)> ")
    print("Please enter new user password again:")
    addconfirmpw = getpass("(Hidden)> ")
    if adduserpw == addconfirmpw:
        user_data[addusername] = {}
        user_data[addusername]["password"] = adduserpw
        user_data[addusername]["admin"] = False
        cprint("User Added!", "green")
        time.sleep(0.3)
        save_data()
        settings()
    else:
        cprint("Password entered is not the same!", "red")
        time.sleep(1)
        settings()

def settings_addplaylist_fetch(playlistId, pageId="", list=[], lastKey=0):
    global song_data
    flagOverflow = False
    url = "https://www.googleapis.com/youtube/v3/playlistItems?key="+YOUTUBE_API_KEY+"&pageToken="+pageId+"&maxResults=50&part=snippet&playlistId="+playlistId
    res = httpx.get(url)
    if res.status_code == httpx.codes.OK:
        clrscr()
        res = res.json()
        for item in res["items"]:
            item_id = item["snippet"]["resourceId"]["videoId"]
            list.append({"id": item_id, "title": item["snippet"]["title"], "preformer": item["snippet"]["videoOwnerChannelTitle"]})
        if pageId == "":
            cprint("Playlist Found!", "green")
            print("")
            print("We have found %s records"%str(len(list)+1))
            if res["pageInfo"]["totalResults"] > (len(list)+1):
                flagOverflow = True
                print("More Items available. Type \"continue\" to fetch more songs.")
            print("")
        i = 1
        for item in list:
            cprint("%s. %s - %s"%(str(i), item["title"], item["preformer"]), "cyan")
            i = i+1
        print("")
        print("Please input command:")
        if flagOverflow:
            print("continue - Fetch more songs to the list")
        print("save - Save all above songs to list and quit")
        print("[int]-[int][,] - Save selection to list and quit")
        print("quit - Quit without saving")
        selection = input("> ")
        if selection == "continue":
            if flagOverflow:
                settings_addplaylist_fetch(playlistId, res["nextPageToken"], list, lastKey)
            else:
                cprint("Unable!", "red")
                time.sleep(1)
                settings_addplaylist()
        elif selection == "save":
            song_data = song_data + list
            save_song()
            cprint("Save Successfully!", "green")
            time.sleep(0.3)
            settings()
        elif containsNumber(selection):
            ranges = selection.split(",")
            try:
                for range in ranges:
                    if "-" in range:
                        range = range.split("-")
                        if not range[0]:
                            range[0] = 1
                        if not range[1]:
                            range[1] = len(list)
                    else:
                        sel = range
                        range = []
                        range[0] = sel
                        range[1] = sel
                    song_data = song_data + list[int(range[0])-1:int(range[1])]
            except KeyError:
                cprint("Out of Range!", "red")
                time.sleep(1)
                settings_addplaylist_fetch(playlistId)
            save_song()
            cprint("Save Successfully!", "green")
            time.sleep(0.3)
            settings()
        elif selection == "quit":
            cprint("Returning to Settings!", "green")
            time.sleep(0.3)
            settings()
        else:
            cprint("Invalid Input!", "red")
            time.sleep(1)
            settings_addplaylist_fetch(playlistId)
    else:
        cprint("Network Error or Playlist Not Found! Error Code: "+str(res.status_code), "red")
        time.sleep(1)
        settings()

def settings_addplaylist():
    clrscr()
    print("")
    print("Add Playlist")
    print("--------------------")
    print("")
    cprint("Only YouTube Playlist URL is supported.", "cyan")
    print("")
    print("Please enter YouTube Playlist URL:")
    playlist_url = input("> ")
    try:
        playlist_id = parse_qs(urlparse(playlist_url).query)["list"][0]
    except KeyError:
        cprint("Unsupported URL!", "red")
        time.sleep(1)
        settings()
    settings_addplaylist_fetch(playlist_id)

def settings_listplaylist():
    global song_data
    clrscr()
    print("")
    print("List Playlist")
    print("--------------------")
    print("")
    i = 1
    for item in song_data:
        cprint("%s. %s - %s"%(str(i), item["title"], item["preformer"]), "cyan")
        i = i+1
    print("")
    print("Please input command:")
    print("del - Save selection to list and quit")
    print("quit - Quit without saving")
    selection = input("> ")
    if selection == "del":
        print("Please enter range ([int]-[int][,]):")
        selection = input("> ")
        if containsNumber(selection):
            ranges = selection.split(",")
            try:
                for range in ranges:
                    if "-" in range:
                        range = range.split("-")
                        if not range[0]:
                            range[0] = 1
                        if not range[1]:
                            range[1] = len(list)
                    else:
                        sel = range
                        range = []
                        range[0] = sel
                        range[1] = sel
                    song_data = song_data[:range[0]] + song_data[range[1]+1:]
            except KeyError:
                cprint("Out of Range!", "red")
                time.sleep(1)
                settings_listplaylist()
            save_song()
            cprint("Save Successfully!", "green")
            time.sleep(0.3)
            settings()
    elif selection == "quit":
        settings()
    else:
        cprint("Invalid Input!", "red")
        time.sleep(1)
        settings_listplaylist()

def settings_admin_edituser():
    global user_data
    clrscr()
    print("")
    print("Edit User")
    print("--------------------")
    print("")
    print("Current Users:")
    for user in user_data:
        cprint(user, "cyan")
    print("")
    print("Please enter username or \"quit\" to exit:")
    selection = input("> ")
    if selection == "quit":
        settings_admin()
    else:
            try:
                user = user_data[selection]
                user = selection
                print("Please enter command:")
                print("epw - Edit Password")
                print("euname - Edit Username")
                print("ep - Edit Points")
                print("pro - Promote to Admin")
                print("de - Demote to user")
                selection = input("> ")
                if selection == "epw":
                    ynpw = input("Are you sure you want to edit your password? Y(yes)/N(no)> ")
                    if (ynpw == "Y" or ynpw =="y"):
                        clrscr()
                        print("Please enter user new password:")
                        newpw = getpass("(Hidden)> ")
                        print("Please enter user new password again:")
                        confirmpw = getpass("(Hidden)> ")
                        if newpw == confirmpw:
                            user_data[user]["password"] = newpw
                            cprint("Password Reset Succesful!", "green")
                            time.sleep(0.3)
                            save_data()
                            settings_admin_edituser()
                        else:
                            cprint("Password entered is not the same!", "red")
                            time.sleep(1)
                            settings_admin_edituser()
                    else:
                        settings_admin_edituser()
                elif selection == "euname":
                    print("Please enter new username:")
                    newusername = input("> ")
                    if newusername in user_data:
                        cprint("Username Taken!", "red")
                        time.sleep(1)
                        settings_admin_edituser()
                    user_data[newusername] = user_data[user]
                    user_data.pop(user)
                    cprint("Username Changed!", "green")
                    time.sleep(0.3)
                    save_data()
                    settings_admin_edituser()
                elif selection == "ep":
                    if "points" in user_data[user]:
                        cprint("Current User "+user+" has "+user_data[user]["points"], "yellow")
                    else:
                        cprint("Current User "+user+" doesn't have points", "red")
                    print("")
                    print("Please enter command:")
                    print("add [int] - Add Points")
                    print("del [int] - Remove Points")
                    print("set [int] - Set Points")
                    selection = input("> ")
                    command = selection.split()[0]
                    value = selection.split()[1]
                    if action == "add":
                        user_data[user]["points"] = user_data[user]["points"] + int(value)
                        cprint("Successful!", "green")
                        time.sleep(0.3)
                        save_data()
                        settings_admin_edituser()
                    elif action == "del":
                        user_data[user]["points"] = user_data[user]["points"] - int(value)
                        cprint("Successful!", "green")
                        time.sleep(0.3)
                        save_data()
                        settings_admin_edituser()
                    elif action == "set":
                        user_data[user]["points"] = int(value)
                        cprint("Successful!", "green")
                        time.sleep(0.3)
                        save_data()
                        settings_admin_edituser()
                    else:
                        cprint("Invalid Input!", "red")
                        time.sleep(1)
                        settings_admin_edituser()
                elif selection == "pro":
                    user_data[user]["admin"] = True
                    cprint("Successful!", "green")
                    time.sleep(0.3)
                    save_data()
                    settings_admin_edituser()
                elif selection == "de":
                    user_data[user]["admin"] = False
                    cprint("Successful!", "green")
                    time.sleep(0.3)
                    save_data()
                    settings_admin_edituser()
                elif selection == "quit":
                    settings_admin_edituser()
                else:
                    cprint("Invalid Input!", "red")
                    time.sleep(1)
                    settings_admin_edituser()
            except KeyError:
                cprint("User Not Found!", "red")
                time.sleep(1)
                settings_admin_edituser()


def settings_admin():
    global user_data
    clrscr()
    print("")
    print("Admin Zone")
    print("--------------------")
    print("1. Edit User")
    print("")
    print("9. Back to Settings")
    print("")
    print("Please select by number:")
    selection = input("> ")
    if selection == "1":
        settings_admin_edituser()
    elif selection == "9":
        settings()
    else:
        cprint("Invalid Input!", "red")
        time.sleep(1)
        settings_admin()

def settings():
    global user_data
    global username
    clrscr()
    print("")
    print("Settings")
    print("--------------------")
    print("1. Reset Password")
    print("2. Add User")
    print("3. Add Song Playlist")
    print("4. List Playlist")
    print("")
    if user_data[username]["admin"]:
        print("8. Admin Zone")
        print("9. Back to Menu")
    elif user_data[username] !=["admin"]:
        print("9. Back to Menu")
    print("")
    print("Please select by number:")
    selection = input("> ")
    if selection == "1":
        settings_resetpw()
    elif selection == "2":
        settings_adduser()
    elif selection == "3":
        settings_addplaylist()
    elif selection == "4":
        settings_listplaylist()
    elif selection == "8":
        settings_admin()
    elif selection == "9":
        menu()
    else:
        cprint("Invalid Input!", "red")
        time.sleep(1)
        settings()

flag_ph = 0
def progress_hook(info):
    global flag_ph
    if info["status"] == "downloading":
        if flag_ph == 0:
            sys.stdout.write(colored("\rDownloading.   %s   "%info["_percent_str"], "cyan"))
            sys.stdout.flush()
            flag_ph = flag_ph + 1
        elif flag_ph == 1:
            sys.stdout.write(colored("\rDownloading..  %s   "%info["_percent_str"], "cyan"))
            sys.stdout.flush()
            flag_ph = flag_ph + 1
        elif flag_ph == 2:
            sys.stdout.write(colored("\rDownloading... %s   "%info["_percent_str"], "cyan"))
            sys.stdout.flush()
            flag_ph = 0
    elif info["status"] == "finished":
        flag_ph = 0
        sys.stdout.write(colored("\rDownloaded. Starting.", "green"))
        sys.stdout.flush()
        time.sleep(0.3)
        clrscr()


def game():
    global user_data
    global song_data
    clrscr()

    if len(song_data) == 0:
        cprint("Playlist missing!", "red")
        time.sleep(1)
        menu()

    if len(song_data) <= 10:
        cprint("Playlist too short! Game may not be fun.", "red")
        time.sleep(0.5)
        print("Press Enter to continue, or type anything to quit")
        selection = input("> ")
        if selection == "":
            clrscr()
        else:
            menu()

    files = os.listdir(SONG_FOLDER)
    for file in files:
        if ".part" in file:
            os.remove(SONG_FOLDER+file)

    qs_song = song_data[random.randrange(len(song_data))]
    if not os.path.isfile(SONG_FOLDER+qs_song["id"]+".mp3"):
        sys.stdout.write(colored("\rLoading...", "cyan"))
        sys.stdout.flush()
        ydl_opts = {
            "format": "bestaudio/best",
            "keepvideo": False,
            "outtmpl": SONG_FOLDER+qs_song["id"]+".%(ext)s",
            "quiet": True,
            "progress_hooks": [progress_hook]
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download(['https://www.youtube.com/watch?v='+qs_song["id"]])

    media_f = ""
    files = os.listdir(SONG_FOLDER)
    for file in files:
        if qs_song["id"] in file:
            media_f = file

    media = vlc.MediaPlayer(SONG_FOLDER+media_f)
    media.play()
    print("")
    print("Game")
    print("--------------------")
    with output(initial_len=3, interval=0) as output_lines:
        i = 0
        while i <= 10:
            if i < len(qs_song["title"]):
                dis_songname = colored(qs_song["title"][0:i] + "_"*(len(qs_song["title"])-i+1)+"     ", "cyan")
            else:
                break
            if i < len(qs_song["preformer"]):
                dis_artistname = colored(qs_song["preformer"][0:i] + "_"*(len(qs_song["title"])-i+1)+"     ", "blue")
            else:
                dis_artistname = qs_song["preformer"]
            output_lines[1] = dis_songname
            output_lines[2] = dis_artistname
            time.sleep(2)
            i = i+1
        output_lines[0] = colored(qs_song["title"], "cyan")
        output_lines[1] = colored(qs_song["preformer"], "blue")
    media.stop()


#Menu as function
def menu():
    clrscr()
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
        settings()
    elif selection == "9":
        sys.exit()
    else:
        cprint("Invalid Input!", "red")
        time.sleep(1)
        menu()

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
        cprint("Login Unsuccessful! Please check your credentials!", "red")
        time.sleep(1)
        login()

login()
