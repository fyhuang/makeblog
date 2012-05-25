import datetime

import post
import twitter

def get_dt(pp):
    if pp[0] == 'blogpost':
        return pp[1].dt
    elif pp[0] == 'twitter':
        return pp[1]['dt']

class Posts(object):
    """Holds all posts and collection data"""
    
    def __init__(self, config):
        self.posts = post.get_blogposts(config)
        self.posts += twitter.get_posts(config)

        self.posts.sort(key=lambda p: get_dt(p), reverse=True)

        self.calc_stats()

    def calc_stats(self):
        # Compute date archive months
        self.post_months = set()
        last_dt = datetime.datetime(1960,01,01)
        for pp in self.posts:
            dt = get_dt(pp)
            if dt.month != last_dt.month or dt.year != last_dt.year:
                self.post_months.add(datetime.datetime(dt.year, dt.month, 01))
            last_dt = dt

        # Compute tags
        self.all_tags = set()
        for pt,p in self.posts:
            if pt != 'blogpost':
                self.all_tags.add(pt)
            else:
                for t in p.tags:
                    self.all_tags.add(t)
