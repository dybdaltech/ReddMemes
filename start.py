import queue, os
import threading, subprocess
import time
import sqlite3
import time
import datetime
import praw
import logging
import json
#import vlc
from zeebees import discord_memes, image_downloader, folder_struct, helper
from single_sub import fill_sub
import settings
import PySimpleGUI as sg
from PIL import Image


def convert_to_png(path):
    """Converts a JPG/JPEG to a PNG. Not used in the current implementation
    does not raise any exceptions, rather crashes the program #TODO: Try/Catch this

    Parameters
    ----------
    Path : str
        string must be a path like string (home/user/documents)

    """
    path = str(path).replace('/', '\\')
    if('.gif' in path or '.mp4' in path):
        path = str(path).replace('\\', '/')
        return path
    else:
        im = Image.open(path)
        basewidth = 1280
        wpercent = (basewidth / float(im.size[0]))
        hsize = int((float(im.size[1]) * float(wpercent)))
        im_resized = im.resize((basewidth, hsize), Image.ANTIALIAS)
        path = str(path).replace('.jpg', '.png')
        path = str(path).replace('.jpeg', '.png')
        path = str(path).replace('.jpg', '.png')
        path= str(path).replace('.png', 'resized_for_bot.png')
        im_resized.save(path)
        return path

#def set_media(player, mediapath, vlc_instance):
#    Media = vlc_instance.media_new_path(mediapath)
#    player.set_media(Media)

def setup_logging():
        
    logger = logging.getLogger(__name__)
    # Create handlers
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler(settings.USER_SETTING['logging_settings']['logfile_name'])
    c_handler.setLevel(logging.DEBUG)
    f_handler.setLevel(logging.INFO)
    # Create formatters and add it to handlers
    c_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - "%(message)s"')
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)
    #Add handlers to the logger
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)
    logger.setLevel(logging.INFO)
    return logger

def main_worker(queue, logger):
    """Primary working thread, accepts a queue object that it outputs to.

    It creates the logger for logging and output to console/GUI
    Uses sqlite3 to save outputs for the front-end viewer

    Parameters
    ----------
    queue : Queue
        A Queue object (from queue module)
    logger : logger
        Instance of the logger object, for logging to output/files

    Raises
    ------
    sqlite3.IntegrityError
        Incase duplicate submissions are scanned. 

    """
    


    queue.put({
        "data":f"Started crawling..",
        "for":"output"
    })
    reddit = praw.Reddit(
        client_id = settings.USER_SETTING['reddit_auth']['client_id'],
        client_secret = settings.USER_SETTING['reddit_auth']['secret'],
        user_agent= settings.USER_SETTING['reddit_auth']['user_agent']
    )

    # DATABASE SETUP: Comment out if you don't need it
    db = helper.database_setup(logger)
    cursor = db.cursor()
    logger.info(f"Auth limits: {reddit.auth.limits}")
    once = False
    logger.info(f"Starting crawling on: {datetime.datetime.now()}")
    while True:
        subreddits_list, subreddits  = helper.load_subreddits(logger, once)
        subreddit = reddit.subreddit(subreddits)
        if once is False:
            logger.info(f"Current watchlist: {subreddit}")
            #Creates the subfolders for downloading
            folder_struct.structure(logger, subreddits_list)
            once = True
            
            queue.put({
                "data":f"Waiting for submissions...",
                "for":"output"
            })
            logger.info("Waiting for submissions...")
        for submission in subreddit.stream.submissions(skip_existing=settings.USER_SETTING["generic_settings"]["skip_existing"], pause_after=10):
            if submission is None:
                logger.info("No submissions; pausing for 10 seconds")
                break
            else:
                if not submission.stickied:
                    if submission.is_self:
                        logger.info(f"Submission: {submission.title} is text post, skipping.")
                        continue
                    logger.info(f'Title: {submission.title} | Subreddit: {submission.subreddit.display_name} | direct url: {submission.url}')
                    queue.put({
                        "data":f'Title: {submission.title} | Subreddit: {submission.subreddit.display_name} | direct url: {submission.url}\n',
                        "for":"output"
                    })
                    is_nsfw = submission.over_18
                    logger.info(f"Over 18? {is_nsfw}")#TODO: Move this into the above logger function. 
                    #TODO: Make this cleaner.
                    if("redd" in submission.url or "imgur" in submission.url or "gfycat" in submission.url):
                        file_output = image_downloader.get_image_raw(f"{submission.url}", submission, is_nsfw, submission.title, submission.permalink, logger)
                        if file_output is None:
                            pass
                        else:
                            data = f"{submission.title}" + " " + file_output
                            queue.put({
                                "data":data,
                                "for":"output"
                            })
                            thumbnail_output = helper.image_file_to_bytes(file_output, (128,128))
                            if thumbnail_output is None:
                                pass
                            else:
                                queue.put({
                                    "data":thumbnail_output,
                                    "for":"image_preview"
                                })
                        try:
                            cursor.execute('''INSERT INTO crawls(url, postId, dir, dateOfEntry, subTitle) VALUES(:url, :postId, :dir, :dateOfEntry, :subTitle)''', {'url':submission.permalink, 'postId':submission.id,'dir':"remove", 'dateOfEntry':str(datetime.datetime.now()), 'subTitle':submission.title})
                        except (sqlite3.IntegrityError, AttributeError) as err:
                            logger.exception("exception occurred")
                    db.commit()
                    logger.info(f"Auth limits: {reddit.auth.limits}")
                    time.sleep(1)
    logger.info(f"Stopped crawling: {datetime.datetime.now()}")

def subreddit_menu():
    subreddits = settings.USER_SETTING['subreddits']
    
    subreddit_menu = []
    for subreddit in subreddits:
        subname = str(subreddit['name'])
        structure = [
            #sg.Text(text=subreddit['tags']),
                [sg.Checkbox(text="",default=subreddit['enabled']), sg.Text(text=f"{subname}", key=f"{subname}"), 
                sg.Button(button_text=f"fill {subname}", key=f"get_subreddit_{subname}")
                ]
                
            ]
        #structure += [[sg.Text(text=subreddit['tags'][i])] for i in range(0, len(subreddit['tags']))]
        subreddit_menu += structure
    last_element = [
        [sg.Text('New subreddit:'), sg.In(key="new_subreddit"), sg.Button('Add', key="add_subreddit") ],
        [sg.Button('Save changes')]
    ]
    subreddit_menu += last_element
    return subreddit_menu

def gui_thread(gui_queue, logger):
    """Main GUI thread, standalone from the main worker thread
    Displays the main graphical user interface

    Parameters
    ----------
    gui_queue : Queue object
        Used to send information from and to the main worker thread
    """
    
    #I need: vlc instance, player instance, video size (standard), a path to file
    video_size = (640, 480)
    scraper_thread = threading.Thread(target=main_worker, args=(gui_queue,logger), daemon=True)
    #starting_path = sg.PopupGetFolder('Folder to display', default_path=settings.USER_SETTING['download_settings']['default_path'])
    starting_path = settings.USER_SETTING['download_settings']['default_path']
    treedata = folder_struct.add_files_in_folder('', starting_path)
    outputTab_layout = [
        [sg.Output(size=(80, 20), key='_OutputMany'), sg.Text(' Preview:'), sg.Image(data='', key='image_preview', size=(128, 128))] #TODO: Add watchlist here! And a enable/disable button?
    ]
    
    #video_layout = [
    #        [sg.Button('STOP', key='stop'), sg.Button('Play/Pause', key='pause'),
    #            sg.Button('Fullscreen', key='full'), sg.Button('Open', key='open'),
    #            sg.Text('Vol', justification='right', size=(10, 1), key='vol')],
    #        [sg.Canvas(key='video_canvas', tooltip='Volume: (Up/Down)\n∓5 seconds: (Left/Right)',
    #            background_color='black', size=video_size)]
    #]
    
    
    
    #subreddit_menu = [
    #    [sg.Checkbox(text=f"{subreddits_list[i]}")] for i in range(0, len(subreddits_list))
    #]
    filesTab_layout = [
        [sg.Text('Files in download')], #TODO: What in the holy christ is this!?
        [sg.Tree(data=settings.DOWNLOAD_FOLDER, headings=['Size','Time'], auto_size_columns=True, num_rows=20, col0_width=30, col_widths=[60, 10, 60], key='_TREE_', show_expanded=False, enable_events=True), 
        sg.Image(data='', key='image', size=(300, 300)), sg.Text('', key='tree_item'), #sg.Canvas(key='video_canvas', tooltip='Volume: (Up/Down)\n∓5 seconds: (Left/Right)',
                #background_color='black', size=video_size)
                ],
            [sg.Button('STOP', key='stop'), sg.Button('Play/Pause', key='pause'),
                sg.Button('Fullscreen', key='full'), sg.Button('Open', key='open'),
                sg.Text('Vol', justification='right', size=(10, 1), key='vol')],
            [sg.Text('')]
    ]
    
    #Settings for the setting window:
    col_text_size = (50, 1)
    col_setting = [
        [sg.Text('Folder settings')],
        [sg.Text('Custom directory', size=col_text_size), sg.InputText(key='config_custom_dir')],
        [sg.Checkbox(text='Is folders setup?',key='config_done_dir')],
        [sg.Text('')],
        [sg.Text('Download settings')],
        [sg.Text('Logfile Name', size=col_text_size), sg.InputText(key='config_logfile_name')],
        [sg.Text('Custom Directory', size=col_text_size), sg.InputText(key='config_custom_logdir')],
        [sg.Text('')],
        [sg.Text('Download settings')],
        [sg.Text('Custom Directory:', size=col_text_size), sg.InputText(key='config_download_dir')],
        [sg.Text('')],
        [sg.Text('Other settings')],
        [sg.Checkbox(text="Display NSFW?",key='config_display_nsfw')],
        [sg.Text('')],
        [sg.Button('Save Settings', key='save_settings')],
        [sg.Text('Some settings will not take effect until you restarted the app!')]
    ]
    setting_layout = [
        [sg.Column(col_setting)]
    ]
    layout = [
        [sg.Text("Meme delivery", size=(10, 1), justification="left")],
        [sg.Text("_"*30, size=(40, 1))],
        [sg.Text('Currently: '),sg.Text('', size=(80, 1), key='_Output')],#sg.Image('', key='image', size=(10, 10)
        [sg.Button('Start'), sg.Button('Exit'), sg.Button('Open'), sg.Button('Refresh', key="Refresh")],
        [sg.TabGroup([
            [
                sg.Tab('Output', outputTab_layout), 
                sg.Tab('Subreddits', subreddit_menu()), 
                sg.Tab('Files', filesTab_layout), 
                sg.Tab('Settings', setting_layout)
            ]
        ])],
    ]
    window = sg.Window('MT bot', resizable=True).Layout(layout)
    
    """
    The main loop
    Reads events every 100 millisecond.

    An event is sent when the loop registers a click, the event is
    equal to the key value of the pressed object. Or the key value of a 
    key pressed.
    """
    #vlc_instance = vlc.Instance('--no-xlib')
    #player = vlc_instance.media_player_new()
    #video_canvas = window['video_canvas'].TKCanvas
    #player.set_hwnd(video_canvas.winfo_id())
    load_settings = False
    while True:
        event, values = window.Read(timeout=100)
        if load_settings is False:
            window.Element('config_custom_dir').Update(value=settings.USER_SETTING['folder_settings']['custom_dir'])
            window.Element('config_logfile_name').Update(value=settings.USER_SETTING['logging_settings']['logfile_name'])
            window.Element('config_custom_logdir').Update(value=settings.USER_SETTING['logging_settings']['custom_dir'])
            window.Element('config_download_dir').Update(value=settings.USER_SETTING['download_settings']['default_path'])
            
            temp_done_bool = 0
            if settings.USER_SETTING['folder_settings']['has_setup'] is True:
                temp_done_bool = 1
            else:
                temp_done_bool = 0
            if settings.USER_SETTING['generic_settings']['display_nsfw'] is True:
                temp_nsfw_bool = 1
            else:
                temp_nsfw_bool = 0
            window.Element('config_display_nsfw').Update(value=temp_nsfw_bool)
            window.Element('config_done_dir').Update(value=temp_done_bool)
            load_settings = True
        if event is None or event == 'Exit':
            #if player.is_playing():
            #    player.stop()
            break
        if event == 'Start':
            #scraper_thread = threading.Thread(target=main_worker, args=(gui_queue,), daemon=True)
            scraper_thread.start()
            print("Starting bot....")
        if event is 'Open':
            selected_item = values.get('_TREE_')
            os.system("start " + str(selected_item[0]))
        if event is '_TREE_':
            selected_item = values.get('_TREE_')
            if 'jpeg' in selected_item[0] or '.png' in selected_item[0] or '.jpg' in selected_item[0]:
                p = helper.image_file_to_bytes(selected_item[0], (300,300))
                window.Element('image').Update(visible=True)
                window.Element('image').Update(data=p, size=(300, 300))
            #elif '.mp4' in selected_item[0]:
                #fpath = helper.create_valid_path(selected_item[0])
                #set_media(player, fpath, vlc_instance)
                #player.play()
        if event is 'Refresh':
            #folder_struct.add_files_in_folder('', starting_path)
            #settings.USER_SETTING.dump(settings.USER_SETTING)
            window.Refresh()
        if "get_subreddit_" in event:
            #scraper_thread = threading.Thread(target=main_worker, args=(gui_queue,logger), daemon=True)
            subreddit_to_fill = event.replace('get_subreddit_', '')
            get_sub_scanner = threading.Thread(target=fill_sub, args=(subreddit_to_fill,), daemon=True)
            get_sub_scanner.start()
        if event is 'save_settings':
            is_folder_setup = window.Element('config_done_dir').Get()
            if is_folder_setup == 1:
                settings.USER_SETTING['folder_settings']['has_setup'] = True
            else:
                settings.USER_SETTING['folder_settings']['has_setup'] = False
            if window.Element('config_display_nsfw').Get() == 1:
                settings.USER_SETTING['generic_settings']['display_nsfw'] = True
            else:
                settings.USER_SETTING['generic_settings']['display_nsfw'] = False
            settings.USER_SETTING['folder_settings']['custom_dir'] = window.Element('config_custom_dir').Get()
            settings.USER_SETTING['logging_settings']['logfile_name'] = window.Element('config_logfile_name').Get()
            settings.USER_SETTING['logging_settings']['custom_dir'] = window.Element('config_custom_logdir').Get()
            settings.USER_SETTING['download_settings']['default_path'] = window.Element('config_download_dir').Get()
            json.dump(settings.USER_SETTING, open('user_configuration.json', 'w'))
            #Get element value in window, set the dictionary variable to the corresponding value
            helper.reload_user_settings() #Reload the settings. a WIP 
        
        while True: #Loop through all messages in the queue coming from threads
            try:
                msg = gui_queue.get_nowait()
            except queue.Empty:
                break
            if msg["for"] == "output":
                try:
                    window.Element('_Output').Update(msg["data"])
                    window.Element('_OutputMany').Update(msg["data"])
                    window.Refresh()
                except:
                    window.Element('_Output').Update("character * is above the range (U+0000-U+FFFF) allowed by Tcl")
                    window.Element('_OutputMany').Update("character * is above the range (U+0000-U+FFFF) allowed by Tcl")
                    window.Refresh()
            if msg["for"] == "image_preview":
                window.Element("image_preview").Update(data=msg["data"])
        #window.Element('config_custom_dir').Update(value=settings.USER_SETTING['folder_settings']['has_setup'])
    window.Close()

#MAIN THREAD
if __name__ == '__main__':
    """
    Initalising the user settings and starts both the
    GUI and worker thread. Passing the gui_queue parameter. 
    """
    logger = setup_logging()
    settings.initialise()
    #Create queue
    gui_queue = queue.Queue()
    #Start the gui passing in the queue
    gui_thread(gui_queue, logger)
    print("Exiting..")

