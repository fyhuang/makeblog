try:
    import configparser
except ImportError:
    import ConfigParser as configparser

import os
import os.path
import sys
import shutil

from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import TemplateNotFound
from scss import Scss

from post import *

class Config(object):
    def __init__(self, filename, dirname, cp):
        self.cp = cp
        self.filename = filename
        self.dirname = dirname

        self.outputdir = os.path.normpath(os.path.join(self.dirname, cp.get('output', 'outputdir')))

    def get(self, section, key):
        return self.cp.get(section, key)

    def getdef(self, section, key, defaultval):
        try:
            return self.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return defaultval

    def pathto(self, path):
        return os.path.join(self.dirname, path)

    def outpathto(self, path):
        result = os.path.join(self.outputdir, path)
        return result

def load_config(filename):
    config_dir = os.path.dirname(os.path.abspath(filename))

    cp = configparser.SafeConfigParser()
    cp.read(filename)

    if not cp.get('output', 'wordpress_compat'):
        print("TODO: needs wordpress_compat")
        sys.exit(1)

    return Config(filename, config_dir, cp)


def get_all_tags(posts):
    tags = set()
    for p in posts:
        for t in p.tags:
            if t not in tags:
                tags.add(t)
    return tags


def makedirs(d):
    try:
        os.makedirs(d)
    except os.error:
        pass

def template_get_asset(config):
    def tga(url):
        return config.get('output', 'prefix').rstrip('/') + '/assets/' + url.lstrip('/')
    return tga

def template_get_url(config):
    def tgu(url):
        return config.get('output', 'prefix').rstrip('/') + '/' + url.lstrip('/')
    return tgu

def load_templates(config):
    env = Environment(loader=FileSystemLoader(config.pathto('templates')))
    env.globals['get_asset'] = template_get_asset(config)
    env.globals['get_url'] = template_get_url(config)

    # TODO: support default, etc.
    templates = {}
    for t in ['index', 'post', 'tag']:
        tname = config.get('templates', t)
        if not tname:
            print("Warning: missing template def " + t)
            continue

        try:
            templates[t] = env.get_template(tname)
        except TemplateNotFound as e:
            print("Warning: template " + e.name + " not found!")

    return templates

def update_assets(config):
    adir = config.pathto('assets')
    if not os.path.exists(adir):
        print("Warning: no assets directory")
        return

    scss = Scss()

    outdir = config.outpathto('assets')
    for (dirpath, dirnames, filenames) in os.walk(adir):
        for fn in filenames:
            sfn = os.path.join(dirpath, fn)
            ddir = os.path.join(outdir, dirpath[len(adir):].lstrip('/'))
            makedirs(ddir)
            dfn = os.path.join(ddir, fn)

            ext = sfn[sfn.rindex('.')+1:]
            if ext == "scss":
                dfn = dfn[:-4] + 'css'
                print("Converting {} to {}".format(sfn, dfn))
                with open(sfn, 'r') as sf, open(dfn, 'w') as df:
                    df.write(scss.compile(sf.read()))
            else:
                print("Copying {} to {}".format(sfn, dfn))
                shutil.copyfile(sfn, dfn)

def update_index(config, posts=None, templates=None):
    if posts is None:
        posts = load_all_posts(config)
    if templates is None:
        templates = load_templates(config)

    print("Writing index")
    page_size = config.getdef('output', 'page_size', 10)

    index_content = templates['index'].render(posts=posts[:page_size])
    with open(config.outpathto('index.html'), 'w') as f:
        f.write(index_content)

def update_tag(config, tag, posts=None, templates=None):
    if posts is None:
        posts = load_all_posts(config)
    if templates is None:
        templates = load_templates(config)

    print("Writing tag page " + tag)
    matching_posts = []
    for p in posts:
        if tag in p.tags:
            matching_posts.append(p)
    page_content = templates['tag'].render(tag=tag, posts=matching_posts)

    makedirs(config.outpathto('tag/'+tag))
    with open(config.outpathto('tag/'+tag+'/index.html'), 'w') as f:
        f.write(page_content)

def update_all(config):
    makedirs(config.outpathto(''))

    update_assets(config)

    posts = load_all_posts(config)
    templates = load_templates(config)

    print("Writing posts")
    for post in posts:
        date_dir = config.outpathto(post.dt.strftime('%Y/%m'))
        post_dir = os.path.join(date_dir, post.slug)
        makedirs(post_dir)

        tpl_content = templates['post'].render(post=post)
        html_fname = os.path.join(post_dir, 'index.html')
        with open(html_fname, 'w') as hf:
            hf.write(tpl_content)

    update_index(config, posts, templates)

    tags = get_all_tags(posts)
    for t in tags:
        update_tag(config, t, posts, templates)
