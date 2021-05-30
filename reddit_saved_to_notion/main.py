import os
import pandas as pd
import sys
from pandas.errors import EmptyDataError
from datetime import date, datetime
import praw
from prawcore.exceptions import OAuthException, ResponseException
from praw.models import Comment
from notion_client import Client, errors
from pprint import pprint
import configparser

config = configparser.ConfigParser()
try:
    config.read_file(open("config.ini", "r"))
    print("Found the config file")
except FileNotFoundError as e:
    print(e)
    print("Please check if the config.ini file is in the root of project")
    sys.exit(1)
notion_token = config["DEFAULT"]["notion_secret"]
database_id = config["DEFAULT"]["database_id"]
kwargs = dict(client_id=config.get('REDDIT', 'client_id'),
              client_secret=config.get('REDDIT', 'client_secret'),
              password=config.get('REDDIT', 'password'),
              username=config.get('REDDIT', 'username'))
username = config.get('REDDIT', 'username')

saved_posts_list = []

try:
    client = Client(auth=notion_token)
    database = client.databases.query(database_id=database_id)
    print("Successfully authenticated with Notion...")
except errors.APIResponseError as e:
    print(e)
    print("Please check the values in the config file")
    sys.exit(1)

reddit = praw.Reddit(**kwargs, user_agent="bot by"+username)

try:
    reddit.user.me()
    print("Successfully authenticated with reddit ...")
except (OAuthException, ResponseException) as e:
    print("Failed to login...Please check your config file")
    sys.exit(1)

check = False

if os.path.isfile("saved_posts.csv"):
    check = True
    try:
        df = pd.read_csv("saved_posts.csv")
        print("Filename saved_posts.csv found.Using it...")
    except EmptyDataError as e:
        print(e)
        print("Please delete the saved_posts.csv file and rerun the script")
        sys.exit(1)
else:
    df = pd.DataFrame()
    print("Existing saved_posts.csv file not found.Creating it...")

for item in reddit.user.me().saved(limit=None):
    if check:
        if df["ID"].str.match(item.id).any():
            print(f"Skipping item id-{item.id} since it already exists...")
            continue
    d = {}
    d['ID'] = item.id
    d["subreddit"] = item.subreddit.display_name
    if isinstance(item, Comment):
        comment = reddit.comment(id=item.id)
        d["url"] = "https://www.reddit.com"+comment.permalink
        d["Title"] = comment.submission.title
        created_utc = datetime.fromtimestamp(comment.created_utc)
        d["Date"] = created_utc.strftime("%Y-%m-%d")
        d["type"] = "Comment"
    else:
        submission = reddit.submission(item.id)
        d["url"] = "https://www.reddit.com"+submission.permalink
        d["Title"] = submission.title
        d["type"] = "Post"
        created_utc = datetime.fromtimestamp(submission.created_utc)
        d["Date"] = created_utc.strftime("%Y-%m-%d")
    new_record = {'ID':
                  {
                      'type': 'rich_text',
                      'rich_text': [{'type': 'text', 'text': {'content': d["ID"], 'link': None},
                                     }]},
                  'Link':
                  {'type': 'url', 'url': d["url"]},
                  'Subreddit': {
                      'type': 'rich_text',
                      'rich_text': [{'type': 'text',
                                     'text': {'content': d["subreddit"], 'link': None},
                                     }]},
                  'Date': {
                      'type': 'date',
                      'date': {'start': d["Date"], 'end': None}},
                  'Title': {
                      'type': 'title',
                      'title': [{'type': 'text',
                                 'text': {'content': d["Title"], 'link': None},
                                 }
                                ]},
                  'Type': {
                      'type': 'rich_text',
                      'rich_text': [{'type': 'text',
                                     'text': {'content': d["type"], 'link': None},
                                     }]}}
    client.pages.create(parent={"database_id":database_id},properties=new_record)
    print(f"Updated record with id-{item.id} in Notion")
    saved_posts_list.append(d)
df = df.append(saved_posts_list, ignore_index=True)
df.to_csv("saved_posts.csv", index=False)
print("Saved posts written to file.")
