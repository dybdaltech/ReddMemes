import re
import os
import json
from zeebees.colors import colors
c = colors()
example_config_file = open('user_configuration copy.json', 'r+')
example_config = json.load(example_config_file)
#1. Ask if you want to setup reddit monitoring
#if yes then ask for reddit auths
#if no skip
#2. ask for custom folder settings
#3. ask for custom donwload path settings (default to current dir + public + images)
#4. ask for new subreddits
yesses = ['yes', 'ye', 'y', '1']
nosses = ['no', 'n', '0']
print(c.fg.green + '-- Redditcrawler setup --')

print(c.fg.lightcyan + "-- Checking if there are any user_configurations available..")
print(c.fg.lightgrey )

try:
    if os.path.isfile('user_configuration.json'):
        print(f'-- found previous config')
        use_old = input("Use old configuration file? (yes/no): ")
        #while use_old not in yesses or use_old not in nosses:
        #    use_old = input("Use old configuration file? (yes/no): ")
        if use_old in yesses:
            print('-- using old config! ')
            example_config = json.load(open('user_configuration.json'))
        elif use_old in nosses:
            print(c.fg.red + '-- creating new config, warning you will have to set up subreddits again!')
            example_config = json.load(example_config_file)
        else:
            print(' errr')
    else:
        use_old = False
except FileNotFoundError:
    use_old = False

def get_reddit_auth():
    use_old_is_false = False
    if use_old in yesses:
        res = input(c.fg.lightgrey + f" Do you want to use {example_config['reddit_auth']['client_id']}?")
        while res == "":
            res = input(c.fg.lightgrey + f" Do you want to use {example_config['reddit_auth']['client_id']}?")
        if res in yesses:
            use_old_is_false = True
            return True
        else:
            use_old_is_false = True
    
    elif use_old in nosses or use_old_is_false or use_old is False:
        res = input(c.fg.lightgrey + " Do you want to setup reddit monitoring (requires API access)? (yes/no) ")
        while res not in ['yes', 'ye', 'y', 'no', 'n']:
            res = input(c.fg.lightgrey + " Do you want to setup reddit monitoring (requires API access)? (yes/no)")
        if res in yesses:
            reddit_id = input(c.fg.orange + "Client ID: ")
            reddit_secret = input(c.fg.orange + "Secret: ")
            reddit_user_agent = input(c.fg.orange + "User Agent: ")
            print(c.fg.lightgrey + "Reddit Authentication settings saved")
        elif res in nosses:
            pass
        try:
            example_config['reddit_auth']['client_id'] = reddit_id
            example_config['reddit_auth']['secret'] = reddit_secret
            example_config['reddit_auth']['user_agent'] = reddit_user_agent

        except:
            return False
    return True

def get_custom_folder_settings():
    use_old_is_false = False
    if use_old in yesses:
        res = input(f"do you want to use {example_config['folder_settings']['custom_dir']}")
        while res == "":
            res = input(f"do you want to use {example_config['folder_settings']['custom_dir']}")
        if res in yesses:
            return True
        else:
            use_old_is_false = True
    elif use_old in nosses or use_old_is_false:
        cwd = os.getcwd()
        default_path = cwd + "\\public\\images\\"
        res = input(c.fg.lightgrey + f" Custom folder path (enter for default)")
        if res == "":
            example_config['folder_settings']['custom_dir'] = default_path
        else:
            example_config['folder_settings']['custom_dir'] = str(res)
        return True

def generic_settings():
    print("Press enter for default")
    skip_input = input("Skip existing posts? (yes/no): ")
    display_nsfw = input("Display NSFW in interfaces? (yes/no): ")
    send_discord = input("Send notifications to discord? (yes/no): ")
    if skip_input == "":
        skip_input = True
    if skip_input in yesses:
        skip_input = True
    elif skip_input in nosses:
        skip_input = False
    
    if display_nsfw == "":
        display_nsfw = True
    if display_nsfw in yesses:
        display_nsfw = True
    elif display_nsfw in nosses:
        display_nsfw = False
    
    if send_discord == "":
        send_discord = True
    if send_discord in yesses:
        send_discord = True
    elif send_discord in nosses:
        send_discord = False

    example_config['generic_settings']['skip_existing'] = skip_input
    example_config['generic_settings']['display_nsfw'] = display_nsfw
    example_config['generic_settings']['send_discord'] = send_discord

    logfile = input('Logfile name: (name.log): ')
    if logfile == "":
        logfile = "log.log"
    example_config['logging_settings']['logfile_name'] = logfile
    custom_dir = input('Custom directory for log: ')
    cwd = os.getcwd()
    default_path = cwd + "\\logs\\"        
    if custom_dir == "":

        example_config['logging_settings']['custom_dir'] = default_path
    else:
        example_config['logging_settings']['custom_dir'] = custom_dir

    if use_old:
        example_config['subreddits'] = example_config['subreddits']
    return True


get_reddit_auth()
print("")
get_custom_folder_settings()
print("")
generic_settings()
print("")
print(c.fg.lightgreen + " Setup file complete! Run start.py next to start the GUI, or run script.py to run without GUI")
print(c.fg.lightgrey + "")
#
json.dump(example_config, open('user_configuration.json', 'w'))