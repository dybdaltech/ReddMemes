import json
import PySimpleGUI as sg
global DISCORD_IS_BLOCKED
global DISCORD_TIMEEND
global DISCORD_TIMESTART
global DOWNLOAD_FOLDER
global USER_SETTING
DOWNLOAD_FOLDER = sg.TreeData()
DISCORD_IS_BLOCKED = False
DISCORD_TIMESTART = None
#userfile = open('user_configuration.json', 'r+')
with open('user_configuration.json', 'r+') as f:
    USER_SETTING = json.load(f)
    f.close()

def initialise():
    pass


def get_user_setting():
    pass