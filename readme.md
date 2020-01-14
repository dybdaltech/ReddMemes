# Reddit crawler

Run setup.py to create the user_configuration.json file. Remember to add your own subreddits and mark them enabled (doesnt work, manualy edit json with enabled: true), or it will not work!

script.py runs only a console interface version, where it loads the user config and just runs with the usual things (new memes are downloaded, sent to discord). 

start.py runs the GUI interface, still buggy but works, it lets you configure *most* not all user config settings, things that can't be changed:

* Enabling or disabling subreddits
* Preview is a bit buggy, already fixed it but not pushed up yet. 



## upcoming (and notes):

1. Sort between gifs and images (subreddit/gifs and subreddit/images)
2. Create a DB with: (complete)

id, link, directory_location, ups (at the time of download), date 

3. build a front end to browse pictures (take it from pastescraper front-end?)
4. Discord webhook! (Complete)
5. "Dynamic" subreddits, load subreddit list from an external source (.txt file? Foreach line in file: subreddit) (Complete!)
6. Webhook urls, add a subreddit "subscriber" tuples? (complete)
7. Make the discord messages an embed, or atleast add the title to the message for context. (Maybe make it so it shows ups/comments aswell?) (complete)
8. Make Discord messages async, (complete)
9. Make a logfile (complete)
10. make a create folder function to remove the error spam in log files (Fixed)
11. make the create DB function a try/except. (complete)
12. GUI Works (complete)
13. 

crawls(id INTEGER PRIMARY KEY, url TEXT NOT NULL , comments TEXT, dir TEXT, dateOfEntry TEXT)

Project structure:

```
root folder/
    subreddits/
        dndmemes/
            memes.jpeg
    mandatory files
    test/
    zeebees/
        project_support_files
    www/
        nginx_files
    
```


# Single sub

It downloads a single subreddit top 100 image posts! Nothing else. 
 
## Setup structure

A wip for setting up file structures, made it so I could simply set the *bot* up on a linux server where file structures are a bit different. 