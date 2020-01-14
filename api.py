#Serve statics with Nginx
#API will find the correct URL (combination with the db?)
#https://www.nginx.com/resources/wiki/start/index.html
from flask_cors import CORS
from flask import Flask
from flask import render_template
import settings
from zeebees import folder_struct
from zeebees import helper
import sqlite3

app = Flask(__name__)
CORS(app) #Cors errors..

def display_nsfw():
    helper.reload_user_settings()
    return settings.USER_SETTING['generic_settings']['display_nsfw']

def get_all_filepaths(subreddit):
    mpath = settings.USER_SETTING['download_settings']['default_path']
    a = folder_struct.find_all_files('', mpath)
    if a is None:
        print("A IS NONE?")
    files, ids = folder_struct.create_filelink(a, subreddit)
    if files is None:
        print("FILES IS NONE")
    elif ids is None:
        print("IDS IS NONE")
    else:
        print("Nothing wrong?")
    
    return files, ids

def get_count():
    mpath = settings.USER_SETTING['download_settings']['default_path']    
    a = folder_struct.find_all_files('', mpath)
    count = folder_struct.get_subreddit_total_count(a)
    subreddit_count = 0
    subreddits_ = []
    for subreddit in settings.USER_SETTING['subreddits']:
        for s in count:
            if s[0] == subreddit['name']:
                subreddit_nsfw = subreddit['nsfw']
                subreddit_enabled = subreddit['enabled']
                subreddit_items = len(s[1])
                subreddits_.append({
                    "name": subreddit['name'],
                    "enabled": subreddit['enabled'],
                    "items": subreddit_items,
                    "nsfw":subreddit['nsfw']
                })
        subreddit_count = subreddit_count+1

    return subreddits_, subreddit_count

def get_info(ids):
    content_info = []
    c = sqlite3.connect('crawls.db').cursor()
    for sid in ids:
        if sid == "default":
            sid = ids[1]
        try:
            query = 'SELECT * FROM crawls WHERE postId = ?'
            t = (sid,)
            #print(sid)
            c.execute(query, t)
            res = c.fetchone()
        except sqlite3.DatabaseError:
            res = None
        if res is not None:
            content_info.append({
                "id":sid,
                "url":res[2],
                "title":res[6]
            })
        else:
            pass
    c.close()
    #print(content_info)
    return content_info


#Create a link to the reddit post to use as title, base: https://www.reddit.com/r/<subreddit>/file[i]
@app.route('/')
def index():
    counters, subreddit_count = get_count()
    #fs = get_all_filepaths(subreddit)
    #print(fs[0])
    return render_template('index.html', display_nsfw=display_nsfw(), sub=counters)

@app.route('/<subreddit>')
def subreddit(subreddit):
    fs, ids = get_all_filepaths(subreddit)
    #TODO: If the content is nonetype error (if no files found)
    
    submissions = get_info(ids)
    return render_template('subreddit.html', files=fs[0], fsLen=len(fs[0]), submissions=submissions)

if __name__ == '__main__':
    app.run(debug=True, host = '127.0.0.1', port = 8080)
