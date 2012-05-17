# Functions used inside templates

def template_get_asset(config):
    def tga(url):
        return config.get('output', 'prefix').rstrip('/') + '/assets/' + url.lstrip('/')
    return tga

def template_get_url(config):
    def tgu(url):
        return config.get('output', 'prefix').rstrip('/') + '/' + url.lstrip('/')
    return tgu

def template_ptype_template(templates):
    def ptt(ptype):
        return templates[ptype]
    return ptt

def template_pretty_date(dt):
    return dt.strftime("%Y/%m/%d")

def shorten_url(url):
    prefixes = ['http://www.', 'https://www.', 'http://', 'https://']
    for p in prefixes:
        if url.startswith(p):
            return url[len(p):]
    return url

def template_linkify_tweet(tweet):
    text = tweet['text']
    for tco_url, real_url in tweet['urls'].items():
        short_real_url = shorten_url(real_url)
        link = '<a href="{}">{}</a>'.format(real_url, short_real_url)
        text = text.replace(tco_url, link)
    return text
