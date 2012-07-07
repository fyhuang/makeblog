import os.path
from datetime import datetime
import json
import re

import yaml
import requests

import post

TWEETS_FILENAME='dynamic/tweets.yaml'

proxies = {'http': '192.168.77.1:8123'}
tco_re = re.compile('(?P<url>http://t.co/([\w]*))')

def expand_url(url):
    params = {'url': url}
    r = requests.get('http://expandurl.appspot.com/expand', params=params, proxies=proxies)
    expanded = json.loads(r.text)
    if expanded['status'] != 'OK':
        return None
    return expanded['end_url']

def refresh_tweets(config):
    tweets_file = config.pathto(TWEETS_FILENAME)
    if not os.path.exists(tweets_file):
        tweets = []
    else:
        with open(tweets_file) as f:
            tweets = yaml.load(f.read())

    params = {'screen_name': config.get('twitter', 'username'),
            'trim_user': 1,}
    if len(tweets) > 0:
        params['since_id'] = tweets[0]['id']
    r = requests.get(\
            'http://api.twitter.com/1/statuses/user_timeline.json',
            params=params,
            proxies=proxies)

    new_tweets = json.loads(r.text)
    for nt in new_tweets:
        url_map = {}
        urls = tco_re.findall(nt['text'])
        for u in urls:
            url_map[u[0]] = expand_url(u[0])

        t = {
                'id': nt['id'],
                'text': nt['text'],
                'dt': datetime.strptime(nt['created_at'], '%a %b %d %H:%M:%S +0000 %Y'),
                'include': True,
                'urls': url_map,
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
