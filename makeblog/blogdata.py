import datetime
import glob

from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import TemplateNotFound

import post
import twitter
import template_fns

def get_dt(pp):
    if pp[0] == 'blogpost':
        return pp[1].dt
    elif pp[0] == 'twitter':
        return pp[1]['dt']

class Blogdata(object):
    """Holds all posts and collection data"""
    
    def __init__(self, config):
        self.config = config

        self.load_posts()
        self.calc_post_stats()
        self.load_pages()
        self.load_templates()

    def load_posts(self):
        self.posts = post.get_blogposts(self.config)
        self.posts += twitter.get_posts(self.config)

        self.posts.sort(key=lambda p: get_dt(p), reverse=True)

        self.posts_by_slug = {(p.slug, p) for (pt,p) in self.posts if pt == 'blogpost'}

    def calc_post_stats(self):
        # Compute date archive months
        post_months = set()
        last_dt = datetime.datetime(1960,01,01)
        for pp in self.posts:
            dt = get_dt(pp)
            if dt.month != last_dt.month or dt.year != last_dt.year:
                post_months.add(datetime.datetime(dt.year, dt.month, 01))
            last_dt = dt
        self.post_months = list(post_months)

        # Compute tags
        all_tags = set()
        for pt,p in self.posts:
            if pt != 'blogpost':
                all_tags.add(pt)
            else:
                for t in p.tags:
                    all_tags.add(t)
        self.all_tags = list(all_tags)

    def load_pages(self):
        pages = []
        for f in glob.glob(self.config.pathto('pages')+'/*.md'):
            page = post.Post(f,self.config)
            pages.append(page)
        self.pages = pages




    def load_templates(self):
        env = Environment(loader=FileSystemLoader(self.config.pathto('templates')))

        env.globals['blogdata'] = self
        env.globals['user_options'] = self.config.get_user_options()

        env.globals['get_asset'] = template_fns.template_get_asset(self.config)
        env.globals['get_url'] = template_fns.template_get_url(self.config)
        env.globals['pretty_date'] = template_fns.template_pretty_date
        env.globals['linkify_tweet'] = template_fns.template_linkify_tweet

        env.globals['utcnow'] = template_fns.template_utcnow
        env.globals['dt_iso'] = template_fns.template_dt_iso



        templates = {}
        for t in ['index', 'blogpost_page', 'tag_archive', 'atom_feed', 'dt_archive', 'page']:
            tname = self.config.get('templates', t)
            if not tname:
                print("Warning: missing template def " + t)
                continue

            try:
                templates[t] = env.get_template(tname)
            except TemplateNotFound as e:
                print("Warning: template " + e.name + " not found!")

        # Social templates
        for s in ['twitter']:
            tname = self.config.get(s, 'template')
            try:
                templates[s] = env.get_template(tname)
            except TemplateNotFound as e:
                print("Warning: template " + e.name + " not found!")

        self.templates = templates
