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
import settings
import PySimpleGUI as sg
from PIL import Image


def convert_to_png(path):
    """Converts a JPG/JPEG to a PNG. Not used in the current implementation
    does not raise any exceptions, rather crashes the program #TODO: Try/Catch this

    Parameters
    ----------
    Path : str
        string must be a path like object (home/user/documents)

    """
    path = str(path).replace('/', '\\')
    if('.gif' in path or '.mp4' in path):
        path = str(path).replace('\\', '/')
        print(path)
        print("Not a JPEG or JPG. SKIPPING")
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

def main_worker(logger):
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
        print(subreddits)
        subreddit = reddit.subreddit(subreddits)
        if once is False:
            logger.info(f"Current watchlist: {subreddit}")
            #Creates the subfolders for downloading
            folder_struct.structure(logger, subreddits_list)
            once = True
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
                    is_nsfw = submission.over_18
                    logger.info(f"Over 18? {is_nsfw}")#TODO: Move this into the above logger function. 
                    #TODO: Make this cleaner.
                    if("redd" in submission.url or "imgur" in submission.url or "gfycat" in submission.url):
                        file_output = image_downloader.get_image_raw(f"{submission.url}", submission, is_nsfw, submission.title, submission.permalink, logger)
                        if file_output is None:
                            pass
                        else:
                            data = f"{submission.title}" + " " + file_output
                        try:
                            cursor.execute('''INSERT INTO crawls(url, postId, dir, dateOfEntry, subTitle) VALUES(:url, :postId, :dir, :dateOfEntry, :subTitle)''', {'url':submission.permalink, 'postId':submission.id,'dir':"remove", 'dateOfEntry':str(datetime.datetime.now()), 'subTitle':submission.title})
                        except (sqlite3.IntegrityError, AttributeError) as err:
                            logger.exception("exception occurred")
                    db.commit()
    logger.info(f"Stopped crawling: {datetime.datetime.now()}")

if __name__ == "__main__":
    settings.initialise()
    logger = setup_logging()

    main_worker(logger)