import os.path
from datetime import datetime
import json

import yaml
import requests

import post

TWEETS_FILENAME='social/tweets.yaml'

def refresh_tweets(config):
    tweets_file = config.pathto(TWEETS_FILENAME)
    if not os.path.exists(tweets_file):
        tweets = []
    else:
        with open(tweets_file) as f:
            tweets = yaml.load(f.read())

    last_id_q = ''
    if len(tweets) > 0:
        last_id_q = '&since_id={}'.format(tweets[0]['id'])

    proxies = {'http': '192.168.77.1:8123'}
    r = requests.get(\
            'http://api.twitter.com/1/statuses/user_timeline.json?screen_name={}&trim_user=1{}'.format(config.get('social', 'twitter_username'), last_id_q),
            proxies=proxies)

    new_tweets = json.loads(r.text)
    for nt in new_tweets:
        t = {
                'id': nt['id'],
                'text': nt['text'],
                'dt': datetime.strptime(nt['created_at'], '%a %b %d %H:%M:%S +0000 %Y'),
                'include': True,
            }
        tweets.append(t)
    print("Loaded {} new tweets".format(len(new_tweets)))

    tweets.sort(key=lambda t: t['dt'], reverse=True)

    with open(tweets_file, 'w') as f:
        f.write(yaml.dump(tweets, default_flow_style=False))

def get_posts(config):
    tweets_file = config.pathto(TWEETS_FILENAME)
    if not os.path.exists(tweets_file):
        return []
    else:
        with open(tweets_file) as f:
            return [('twitter', t) for t in yaml.load(f.read()) if t['include']]
