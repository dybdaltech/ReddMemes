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

def setup_logging():
        
    logger = logging.getLogger(__name__)
    # Create handlers
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler("single.log")
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

def fill_sub(sub):
    reddit = praw.Reddit(
        client_id = settings.USER_SETTING['reddit_auth']['client_id'],
        client_secret = settings.USER_SETTING['reddit_auth']['secret'],
        user_agent= settings.USER_SETTING['reddit_auth']['user_agent']
    )
    logger = setup_logging()
    db = helper.database_setup(logger)
    cursor = db.cursor()
    logger.info(f"Auth limits: {reddit.auth.limits}")
    once = True
    logger.info(f"Starting crawling on: {datetime.datetime.now()}")
    subreddit = reddit.subreddit(sub)
    for submission in subreddit.top('all'):
        if submission is None:
            logger.info("No submissions; pausing for 10 seconds")
            break
        else:
            title = submission.title
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
                        thumbnail_output = helper.image_file_to_bytes(file_output, (128,128))
                        if thumbnail_output is None:
                            pass
                        else:
                            pass
                    try:
                        cursor.execute('''INSERT INTO crawls(url, postId, dir, dateOfEntry, subTitle) VALUES(:url, :postId, :dir, :dateOfEntry, :subTitle)''', {'url':submission.permalink, 'postId':submission.id,'dir':"remove", 'dateOfEntry':str(datetime.datetime.now()), 'subTitle':submission.title})
                    except (sqlite3.IntegrityError, AttributeError) as err:
                        logger.exception("exception occurred")
                db.commit()
                logger.info(f"Auth limits: {reddit.auth.limits}")
            time.sleep(1)
    logger.info(f"Stopped crawling: {datetime.datetime.now()}")
