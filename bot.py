import praw
from config import *

import re, time, requests, os
import bs4
from peewee import *


db_proxy = Proxy()


class BlacklistUser(Model):
    name = CharField()

    class Meta:
        database = db_proxy


def create_tables():
    if os.getenv('HEROKU'):
        database = PostgresqlDatabase('samplepg.db') # add psycopg2 auth
    else:
        database = SqliteDatabase('blacklist.db')
    db_proxy.initialize(database)


def get_access_token():
    response = requests.post("https://www.reddit.com/api/v1/access_token",
      auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET),
      data = {"grant_type": "password", "username": REDDIT_USER, "password": REDDIT_PASS},
      headers = {"User-Agent": USER_AGENT})
    return response.json()["access_token"]


def get_praw():
    r = praw.Reddit(USER_AGENT)
    r.set_oauth_app_info(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
    r.set_access_credentials(set(AUTH_TOKENS), get_access_token())
    return r


def handle_rate_limit(func, *args, **kwargs):
    while True:
        try:
            func(*args, **kwargs)
            break
        except praw.errors.RateLimitExceeded as error:
            print('\tSleeping for {:d} seconds'.format(error.sleep_time))
            time.sleep(error.sleep_time)


def run_command(comment, search_term):
    try:
        url = BASE_URL + search_term
        url = url.replace(' ', '&')
        req = requests.get(url)
        req.raise_for_status()
    except requests.HTTPError:
        print('HTTP Error occured')
        return
    soup = bs4.BeautifulSoup(req.content)
    if soup.select('.suggestion'):
        return
    else:
        comment_body = ''
        a_tag = soup.select('.toppush1 .mobile-2 span a')[0]
        name = a_tag.getText()
        link = a_tag.get('href')
        if name.lower() != search_term.lower():
            comment_body += "'{:s}' not found, did you mean {:s}?\n".format(search_term, name)
        name = search_term
        comment_body += 'Panjury link for {:s}: \n{:s}'.format(name, link)
        comment.reply(comment_body)
        print('Name: {:s}\tLink: {:s}'.format(name, link))


def check_for_command(comment):
    search = re.search(r'^panjurybot\s+', comment.body.strip(), re.IGNORECASE)
    if search:
        command = comment.body.strip()[len(search.group(0)):]
        kword_1 = re.search(r'^what\s+is\s+(\w+.+)', command)
        kword_2 = re.search(r'^tell\s+me\s+about\s+(\w+.+)', command)
        if kword_1:
            search_term = kword_1.group(1)
        elif kword_2:
            search_term = kword_2.group(1)
        else:
            return
        run_command(comment, search_term)


def main():
    r = get_praw()
    c_stream = praw.helpers.comment_stream(r, SUBREDDIT, limit=100, verbosity=0)
    for comment in c_stream:
        check_for_command(comment)

if __name__ == '__main__':
    try:
        create_tables()
        main()
    except KeyboardInterrupt:
        print('\nStopped by Keyboard interrupt')