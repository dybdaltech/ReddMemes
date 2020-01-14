import queue, os, re
import threading, subprocess
import time
import sqlite3
import time
import datetime
import praw
import logging
import settings
import json
import PySimpleGUI as sg
#from PIL import Image
import io
"""
This is a whole bunch of helper functions for the project, either shamelessly stolen from the interwebs or 
something I mixed up around midnight during a full moon
"""


################################################################
###################  #################

#
def clear_title(data):
    data_ = re.sub('[^a-zA-Z0-9 \n\.]', '', data)
    data_ = ( data_[:32] + ";") if len( data_) > 32 else data_
    return data_

def remove_at(i, s):
    """Takes a int and str, removes char at int position

    Parameters
    ----------
    i : integer, required
        Removes the character at the position of the int
    s : string, required
        The string you want to change

    """
    return s[:i] + s[i+1:]

def load_subreddits(logger, once):
    """Loads the subreddit file, which specifies which subreddits to load

    Parameters
    ----------
    logger : Logging instance
        logging to file and output
    
    once : bool
        I am actually not sure what it does
    
    Returns
    -------
    subreddit_list
        A list containing the loaded subreddits
    
    subreddits_many
        A Multireddit search friendly string, used in creating
        the PRAW search instance
    """

    subreddit_string = ""
    subreddit_list = []
    subreddits = settings.USER_SETTING['subreddits']
    print(subreddits)
    for subreddit in subreddits:
        if subreddit["enabled"]:
            sub_name = subreddit["name"]
            if(once is False):
                logger.info(f"Added {sub_name} to search")
            subreddit_string = subreddit_string + "+" + subreddit["name"]
            subreddit_list.append(subreddit["name"])
    subreddits_many = remove_at(0, subreddit_string)
    #print(subreddits_many)
    return subreddit_list, "dndmemes"

def database_setup(logger):
    """Setups the database for saving the submissions in a friendly manner
    
    Parameters
    ----------
    logger : Logging instance
        logging to file and output

    Returns
    -------
    db
        sqlite3 database instance
    """

    db = sqlite3.connect('crawls.db')
    try:
        db.cursor().execute('''CREATE TABLE IF NOT EXISTS crawls(id INTEGER PRIMARY KEY, postId TEXT UNIQUE NOT NULL ,url TEXT NOT NULL , comments TEXT, dir TEXT, dateOfEntry TEXT, subTitle TEXT)''')
        
    except sqlite3.OperationalError as err:
        logger.exception(f"{err}")
    db.commit()
    return db

################################################################
#################### Image helpers #############################

def create_thumbnail(image):
    """Creates a thumbnail image of a image file

    Parameters
    ----------
    image : String path, required
        A path like string, used for the PIL Image to open the file

    Returns
    -------
    image
        Thumbnail path of the input image
    """

    size = 128, 128
    im = Image.open(image)
    im.thumbnail(size)
    im.save(image + ".thumbnail", "PNG")
    print(image)
    return image

def image_file_to_bytes(filename, size):
    """Converts a image to bytes for the preview

    Parameters
    ----------
    filename : string, required
        A path like string, used for PIL Image to open the file

    size : tuple(x, y), required
        A tuple for the size of the image, set to (128, 128) in the caller

    Raises
    ------
    exception if the file path is wrong

    Returns
    -------
    imgbytes
        The image bytes for the PySimpleGUI image element

    """

    try:
        image = Image.open(filename)
        image.thumbnail(size, Image.ANTIALIAS)
        bio = io.BytesIO()  # a binary memory resident stream
        image.save(bio, format='PNG')  # save image as png to it
        imgbytes = bio.getvalue()
    except:
        imgbytes = None
    return imgbytes

def covnert_to_png(filename):
    """Converts a JPG to PNG
    
    Parameters
    ----------
    filename :  string, required
        A path like string of which image to convert, 
    
    Returns
    -------
    new_filename : string
        
    """
    new_filename = str(filename).replace('.jpg', '.png')
    Image.open(filename).save(new_filename)
    return new_filename



##################################################################
############### Other helper functions ###########################

def selected_tree_item(tree):
    """
    
    """
    current_item = tree.focus()
    print(current_item)

def create_valid_path(path):
    return path.replace('/', '\\')


def reload_user_settings():
    with open('user_configuration.json', 'r+') as f:
        settings.USER_SETTING = json.load(f)
        #print(settings.USER_SETTING)
        f.close()

