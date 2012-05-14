import re

_url_nonchars_re = re.compile('[^\w\-&=]')
_multiple_dashes_re = re.compile('-+')

def title_to_slug(title):
    slug = _url_nonchars_re.sub('-', title).strip('-')
    slug = _multiple_dashes_re.sub('-', slug).lower()
    return slug

def first_posts(posts, maxnum):
    count = 0
    last_ix = 0
    last_pt = ''
    for (pt,p) in posts:
        last_ix += 1
        if not (pt == 'twitter' and last_pt == 'twitter'):
            count += 1
            if count >= maxnum:
                break
        last_pt = pt

    return posts[:last_ix]
