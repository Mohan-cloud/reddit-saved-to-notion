# reddit-saved-to-notion

A way to export your saved reddit posts to a Notion table.Uses [notion-sdk-py](https://github.com/ramnes/notion-sdk-py) and [praw](https://github.com/praw-dev/praw) for interacting with Notion and Reddit respectively.

Writes to csv file. Reddit post is not updated in Notion if it is present in all csv file.

## Pre-requisties
* client_id and client_secret from Reddit. https://github.com/reddit-archive/reddit/wiki/OAuth2-Quick-Start-Example#first-steps
* Follow the instructions [here](https://developers.notion.com/docs/getting-started) to get your notion_secret and database_id.
* Import this [notion template](https://www.notion.so/1d6cadece4d6462ab9e72f98ca1c7558?v=cb2d823167d74f97a914155b8ff7d548)  

## Steps
* Recommended to run in a virtual environment
* If you have `poetry` installed, then execute `poetry install`
* Else run `pip install -r requirements.txt`
* Rename `config_eg.ini` to `config.ini` and fill in the values
* From the root of the directory run, `python3 reddit-saved-to-notion/main.py`

