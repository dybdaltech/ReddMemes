from bs4 import BeautifulSoup
import requests
import shutil, random, re, os, sqlite3, datetime, asyncio, time
import urllib.request
import json
from zeebees import discord_memes, folder_struct, helper
import settings

def folder_setup():
    pass

def validate_img_link(link):
    regex = r"(\/\/)(.*)/(.*)"
    test = re.findall(regex, link)
    return test


def get_extension(url):
    extension_types = [".jpg", ".png", ".gif", ".mp4"]
    if("gfycat" in url):
        return ""
    for ext in extension_types:
        if(ext in url):
            return ext


def clean_filename(link, dirName, submission):
    #title = helper.clear_title(submission.title)
    extension = get_extension(link)
    file_name = str(dirName) + "\\" + submission.id + str(extension)
    return file_name


def get_gfycatlink(url):
    """Because Gfycat is a bit of a special one, it needs its own function
    Copied the base of the code from bulk-downloader-for-reddit on github.

    """
    #url = "https://gfycat.com/lazypolitegiantschnauzer-puppies-dogs"

    if url[-1:] == '/':
        url = url[:-1]

    url = "https://gfycat.com/" + url.split('/')[-1]

    
    try:
        pageSource = (urllib.request.urlopen(url).read().decode())
    except urllib.error.HTTPError as err:
        print("No content found, skipping..")
        return None
    soup = BeautifulSoup(pageSource, "html.parser")
    attributes = {"data-react-helmet":"true","type":"application/ld+json"}
    content = soup.find("script",attrs=attributes)

    if content is None:
        raise NotADownloadableLinkError("Could not read the page source")
    
    return json.loads(content.text)["video"]["contentUrl"]


def get_image_raw(url, submission, nsfw, title, perma, logger):
    """TODO: Split into two functions.
    1. it creates the directory for the submission
    2. Gets the image of the url

    Parameters
    ----------
    url : str, required
        url to retrieve
    submission : Instance of submission, required
        Pass the instance of the submission to use with the script
    nsfw : bool, required
        is the submission NSFW? 
    title : str, required
        gotten from the submission instance, can also use the passed ubreddit
    perma : str, required
        used to create the full link
    logger : Logger instance, required
        For outputting information into the log and output
    """
    gfy = False
    file_path = folder_struct.get_file_path(submission.subreddit.display_name)
    img_link = str(url)
    file_name = clean_filename(img_link, file_path, submission)
    logger.info(f"Saving image as: {file_name}")

    if(os.path.exists(file_name)):
        logger.info(f"File {file_name} already exists, skipping")
    else:
        if(settings.USER_SETTING['generic_settings']['send_discord']):
            if(settings.DISCORD_IS_BLOCKED):
                elapsed = time.time() - settings.DISCORD_TIMESTART
                if(int(elapsed) == 90):
                    settings.DISCORD_IS_BLOCKED = False
                else:
                    logger.info(f"Discord is still blocked, elapsed: {str(elapsed)}")
            else:
                discord_memes.post_to_discord(url, True, nsfw, title, submission.subreddit.display_name, perma, logger)
        else:
            logger.info(f"send to discord is {settings.USER_SETTING['generic_settings']['send_discord']}")
        if("gfycat" in url or ".gif" in url):
            if(".gif" in url):
                file_name = file_name
            else:
                file_name = file_name + ".mp4"
                gfy = True
            with open(file_name, 'wb') as out_file:
                #TODO: Fix for Gfycat
                if(gfy):
                    url = get_gfycatlink(url)
                    if url is None:
                        logger.error(f"No Gfycat found, skipping post {submission.id}")
                    else:
                        logger.info(f"GFYCAT {url} saving to {file_name}")
                        out_file.write(requests.get(url).content)
                        logger.info(f"GFY: URL: {url} | file: {file_name}")
                else:
                    out_file.write(requests.get(url).content)
            logger.info(f"Done saving image {file_name}")
            return str(file_name)
        else:
            if(submission.is_self):
                logger.info("Not a media post, skipping download.")
                return None
            else:
                try:
                    urllib.request.urlretrieve(url, file_name)
                    logger.info(f"URL: {url} | file: {file_name}")
                    return str(file_name)
                except Exception as err:
                    logger.exception(f"Exception in image_downloader: {err}")
                    return None
                #png_file = helper.covnert_to_png(file_name)
            logger.info(f"Done saving image {file_name}")
            return str(file_name)