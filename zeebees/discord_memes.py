import requests
import json
import asyncio
import settings
import datetime, time
def post_to_discord(link, ismeme = True, nsfw = False, title = "", subreddit = "", permalink = "", logger=None):
    """Looks through the Webhook list and sends a Discord message
    if a subreddit is in the webhook dictionary.

    A Webhook list entry can have the 'all' instead of listing a subreddit,
    it then sends a message to the url in the entry. 

    Parameters
    ----------
    link : str, required
        A direct URL for the image post.
    ismeme : bool, optional
        Not implemented yet #TODO: Implement
    nsfw : bool, required
        A bool telling it if the over_18 attribute of submission
        is NSFW or not
    title : str, required
        A string representing the title of the post
        from submission.title
    subreddit : str, required
        String represinting the subreddit of the post
        from submission.subreddit.display_name
    permalink : str, required
        Represents the last part of the submission URL
        from submission.permalink, it creates a full URL before sending
    logger : logging, required
        logging object for logging the output to a logfile and output
    
    """
    webhook_url = ''
    #TODO: External load (json file)
    webhook_urls = [
        {
            "user": "Default (all)", #Username of the server owner
            "url":"", #Webhook url
            "nsfw": False, #Does the server allow NSFW?
            "subreddits":"" #Blank = all subreddits, type the 
        },
        {
            "user": "Default NSFW (all)", #Username of the server owner
            "url": "", #Webhook url
            "nsfw": True, #Does the server allow NSFW?
            "subreddits":"" #Blank = all subreddits, type the 
        }
    ]

    if(nsfw is True):
        data = {
            "username": "NSFW delivery",
            "embeds":[
                {
                    "title": title + ":joy:",
                    "description":str("https://reddit.com"+permalink),
                    "image": {
                        "url":link
                    },
                    "footer":{
                        "text":str(subreddit)
                    },
                    "color": 0xff0000
                }
            ]
        }
    else:
        data = {
            "username": "Auto Meme delivery",
            "embeds":[
                {
                    "title": title + ":joy:",
                    "description":str("https://reddit.com"+permalink),
                    "image": {
                        "url":link
                    },
                    "footer":{
                        "text":f"str(subreddit) | Bot built by Zeay#9501"
                    },
                    "color": 0x00ff27
                }
            ]
        }
    for webhook in webhook_urls:
        if(str(subreddit).lower() in webhook['subreddits'].lower() or webhook['subreddits'] == "all"):
            logger.info(f"Is in subscribers subreddit list for: {webhook['user']}")
            if(nsfw and webhook['nsfw']):
                result = requests.post(webhook['url'], data=json.dumps(data), headers={"Content-Type": "application/json"})
                logger.info(f"Sent embed to: {webhook['user']}")
                try:
                    result.raise_for_status()
                except requests.exceptions.HTTPError as err:
                    # This entire thing is a work in progress, not sure if it even works (I think it does, have yet to be limited/blocked!)
                    logger.exception("Discord exception - setting timeout")
                    settings.DISCORD_IS_BLOCKED = True
                else:
                    logger.info(f"Sent meme alert, code {result.status_code} (NSFW)")
            elif(nsfw is False and webhook['nsfw'] is False):
                result = requests.post(webhook['url'], data=json.dumps(data), headers={"Content-Type": "application/json"})
                logger.info(f"Sent embed to: {webhook['user']}")
                try:
                    result.raise_for_status()
                except requests.exceptions.HTTPError as err:
                    # This entire thing is a work in progress, not sure if it even works (I think it does, have yet to be limited/blocked!)
                    logger.exception("Discord Exception - setting timeout")
                    settings.DISCORD_IS_BLOCKED = True
                    settings.DISCORD_TIMESTART = time.time()
                else:
                    logger.info(f"Sent meme alert, code {result.status_code}")
        else:
            pass