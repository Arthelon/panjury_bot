config_file = open('assets/secret.txt', 'rt')
config = config_file.read().splitlines()
config_file.close()

REDDIT_USER = config[0]
REDDIT_PASS = config[1]
CLIENT_ID = config[2]
CLIENT_SECRET = config[3]
REDIRECT_URI = 'http://127.0.0.1:65010/authorize_callback'

# Configuration Settings
USER_AGENT = "macosx:panjury_test_app:0.0.1 (by /u/Arthelon)"
SUBREDDIT = "pythonforengineers"
AUTH_TOKENS = ['read', 'submit']

BASE_URL = 'http://www.panjury.com/search/index/keyword/'
