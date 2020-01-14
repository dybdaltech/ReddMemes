import os
import PySimpleGUI as sg
import settings
import time
import re
folder_icon = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsSAAALEgHS3X78AAABnUlEQVQ4y8WSv2rUQRSFv7vZgJFFsQg2EkWb4AvEJ8hqKVilSmFn3iNvIAp21oIW9haihBRKiqwElMVsIJjNrprsOr/5dyzml3UhEQIWHhjmcpn7zblw4B9lJ8Xag9mlmQb3AJzX3tOX8Tngzg349q7t5xcfzpKGhOFHnjx+9qLTzW8wsmFTL2Gzk7Y2O/k9kCbtwUZbV+Zvo8Md3PALrjoiqsKSR9ljpAJpwOsNtlfXfRvoNU8Arr/NsVo0ry5z4dZN5hoGqEzYDChBOoKwS/vSq0XW3y5NAI/uN1cvLqzQur4MCpBGEEd1PQDfQ74HYR+LfeQOAOYAmgAmbly+dgfid5CHPIKqC74L8RDyGPIYy7+QQjFWa7ICsQ8SpB/IfcJSDVMAJUwJkYDMNOEPIBxA/gnuMyYPijXAI3lMse7FGnIKsIuqrxgRSeXOoYZUCI8pIKW/OHA7kD2YYcpAKgM5ABXk4qSsdJaDOMCsgTIYAlL5TQFTyUIZDmev0N/bnwqnylEBQS45UKnHx/lUlFvA3fo+jwR8ALb47/oNma38cuqiJ9AAAAAASUVORK5CYII='
file_icon = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsSAAALEgHS3X78AAABU0lEQVQ4y52TzStEURiHn/ecc6XG54JSdlMkNhYWsiILS0lsJaUsLW2Mv8CfIDtr2VtbY4GUEvmIZnKbZsY977Uwt2HcyW1+dTZvt6fn9557BGB+aaNQKBR2ifkbgWR+cX13ubO1svz++niVTA1ArDHDg91UahHFsMxbKWycYsjze4muTsP64vT43v7hSf/A0FgdjQPQWAmco68nB+T+SFSqNUQgcIbN1bn8Z3RwvL22MAvcu8TACFgrpMVZ4aUYcn77BMDkxGgemAGOHIBXxRjBWZMKoCPA2h6qEUSRR2MF6GxUUMUaIUgBCNTnAcm3H2G5YQfgvccYIXAtDH7FoKq/AaqKlbrBj2trFVXfBPAea4SOIIsBeN9kkCwxsNkAqRWy7+B7Z00G3xVc2wZeMSI4S7sVYkSk5Z/4PyBWROqvox3A28PN2cjUwinQC9QyckKALxj4kv2auK0xAAAAAElFTkSuQmCC'

def structure(logger, subreddits):
    #print("Setting folders..")
    if settings.USER_SETTING["folder_settings"]["custom_dir"] is None or len(settings.USER_SETTING["folder_settings"]["custom_dir"]) < 2:
        print("Custom dir is none")
        cwd = os.getcwd()
        subdir = cwd + "\\downloads" + "\\"
        logger.info(f"Using default directory {subdir}")
    else:
        print("Using custom dir")
        subdir = settings.USER_SETTING["folder_settings"]["custom_dir"]
        logger.info(f"Using custom directory {subdir}")
    failed_dirs = ""
    #print(settings.USER_SETTING['folder_settings']['has_setup'])
    if(settings.USER_SETTING['folder_settings']['has_setup'] is False):
        for subreddit in subreddits:
            folder_path = subdir+str(subreddit)
            try:
                os.mkdir(folder_path)
            except OSError:
                failed_dirs = failed_dirs + " " + str(subreddit)
            else:
                logger.info(f"Created folder: {folder_path}")
    else:
        logger.info("already setup folders.")
        pass
    if failed_dirs:
        logger.warning(f"Failed to create directories: {failed_dirs}")


def get_file_path(subreddit_name):
    file_path = settings.USER_SETTING["folder_settings"]["custom_dir"]
    if file_path is None or len(settings.USER_SETTING["folder_settings"]["custom_dir"]) < 2:
        return os.getcwd() + "\\" + "downloads" + "\\" + str(subreddit_name)
    else:
        return settings.USER_SETTING["folder_settings"]["custom_dir"] + str(subreddit_name)
    pass

def add_files_for_tree_view(parent, dirname):
    files = os.listdir(dirname)
    treedata = sg.TreeData()
    for f in files:
        fullname = os.path.join(dirname,f)
        fullname = fullname.replace('/', '\\')
        if os.path.isdir(fullname):            # if it's a folder, add folder and recurse
            treedata.Insert(parent, fullname, f, values=[], icon=folder_icon)
            add_files_for_tree_view(fullname, fullname)
        else:
            treedata.Insert(parent, fullname, f, values=[os.stat(fullname).st_size, os.stat(fullname).st_mtime], icon=file_icon)
    return treedata

def add_files_in_folder(parent, dirname):
    files = os.listdir(dirname)
    return_value = []
    for f in files:
        fullname = os.path.join(dirname,f)
        if os.path.isdir(fullname):            # if it's a folder, add folder and recurse
            settings.DOWNLOAD_FOLDER.Insert(parent, fullname, f, values=[], icon=folder_icon)
            #return_value.insert(parent, fullname)
            add_files_in_folder(fullname, fullname)
        else:
            settings.DOWNLOAD_FOLDER.Insert(parent, fullname, f, values=[os.stat(fullname).st_size, time.ctime(os.path.getmtime(fullname))], icon=file_icon)


def find_all_files(parent, dirname):
    files = os.listdir(dirname)
    return_value = []
    obj = {
        'parent':[
            'file',
            'file'
        ]
    }
    for f in files:
        fullname = os.path.join(dirname,f)
        if os.path.isdir(fullname):            # if it's a folder, add folder and recurse
            foldername = re.search(r"(.*\\)(.*)", fullname)
            items = find_filenames(fullname, fullname)
            return_value.append([foldername[2], items])
    return return_value

def find_filenames(parent, dirname):
    files = os.listdir(dirname)
    objects = []
    for f in files:
        objects.append(f)
    return objects

def id_of_post(file):
    r = r"(.*)\.(.*)"
    post_id = re.search(r, file)
    try:
        if post_id is None:
            post_id = "default"
        else:
            post_id = post_id[1]
            #print(f"ID OF POST IS: {post_id}")
    except re.error as err  :
        print(err)
    return post_id

def create_hyperlink_for_file(files, directory):
    hl_files = []
    id_files = []
    site = 'http://192.168.10.125/images/' + directory
    for file in files:
        #print(site+ "/"+ file)
        hl_files.append(site + "/" + file)
        id_files.append(id_of_post(file))
    return hl_files, id_files


def create_filelink(filepaths, subreddit): #what if we mention the subreddit first?
    for folder in filepaths:
        if len(folder[1]) > 1:
            if folder[0] == subreddit:
                a, ids = create_hyperlink_for_file(folder[1], folder[0])
                #print(a)
                #print(ids)
                rt = [a]
                return rt, ids

def get_subreddit_total_count(filepaths):
    counter_list = []
    subreddit = 'all'
    if subreddit is "all":
        for folder in filepaths:
            counter_list.append(folder)
        return counter_list