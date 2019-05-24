import os
import random
import re
import time
from datetime import datetime
import praw
from praw import exceptions as praw_exceptions
from loguru import logger
import json
from utils.dataIO import dataIO




def initalize():
    global reddit


    try:
        reddit = praw.Reddit(client_id=config['reddit']['client_id'],
                             client_secret=config['reddit']['client_secret'],
                             password=config['reddit']['password'],
                             user_agent=config['reddit']['user_agent'],
                             username=config['reddit']['username'])
    except:
        logger.error("Reddit unable to login, check credentials in auth.ini file")
        exit(code=1)

def check_folders():
    if not os.path.exists("data/watchparty"):
        logger.info("Creating data/watchparty folder...")
        os.makedirs("data/watchparty")

def check_files():
    if not dataIO.is_valid_json("data/watchparty/subscribed_users.json"):
        logger.debug("Creating empty subscribed_users.json...")
        dataIO.save_json("data/watchparty/subscribed_users.json", [])




def scan_comments(subreddit):
    for comment in subreddit.comments(limit=25):
        if comment.body.lower() == "!subscribe" and comment.author.name not in users_subscribed:
            # user wants to subscribe to the list
            try:
                logger.info(f"User {comment.author.name} has subscribed!")
                add_user(comment.author, subreddit)
                confirm_subscription(comment)
            except praw_exceptions.APIException as e:
                logger.error(e.error_type + e.message)
                pass



def confirm_subscription(comment):
    mail = comment.author.message(config['mail']['subject'], config['mail']['body'])
    return mail

def add_user(user, subreddit):
    subbies.append(
        {"user": user.name, "subreddit": subreddit.title, "date_added": str(datetime.now())})
    dataIO.save_json("data/watchparty/subscribed_users.json", subbies)

def remove_user(user):
    pass

if __name__ == "__main__":
    check_folders()
    check_files()
    subbies = dataIO.load_json('data/watchparty/subscribed_users.json')
    config = dataIO.load_json("config.json")
    users_subscribed = [x['user'] for x in subbies]
    initalize()
    while True:
        for subreddit in config['subreddits']:
            sub = reddit.subreddit(subreddit)
            scan_comments(sub)