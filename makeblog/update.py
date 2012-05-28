import os
import os.path
import sys
import shutil
import datetime

from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import TemplateNotFound
from scss import Scss

from post import *
from data import *
import utils
import template_fns
import twitter

def makedirs(d):
    try:
        os.makedirs(d)
    except os.error:
        pass

def load_templates(config):
    env = Environment(loader=FileSystemLoader(config.pathto('templates')))

    # TODO: support default, etc.
    templates = {}
    for t in ['index', 'blogpost_page', 'tag_archive', 'atom_feed', 'dt_archive', 'page']:
        tname = config.get('templates', t)
        if not tname:
            print("Warning: missing template def " + t)
            continue

        try:
            templates[t] = env.get_template(tname)
        except TemplateNotFound as e:
            print("Warning: template " + e.name + " not found!")

    # Social templates
    for s in ['twitter']:
        tname = config.get(s, 'template')
        try:
            templates[s] = env.get_template(tname)
        except TemplateNotFound as e:
            print("Warning: template " + e.name + " not found!")

    env.globals['user_options'] = config.get_user_options()

    env.globals['get_asset'] = template_fns.template_get_asset(config)
    env.globals['get_url'] = template_fns.template_get_url(config)
    env.globals['pretty_date'] = template_fns.template_pretty_date
    env.globals['ptype_template'] = template_fns.template_ptype_template(templates)
    env.globals['linkify_tweet'] = template_fns.template_linkify_tweet

    env.globals['utcnow'] = template_fns.template_utcnow
    env.globals['dt_iso'] = template_fns.template_dt_iso

    return templates

def load_pages(config):
    import glob
    pages = []
    for f in glob.glob(config.pathto('pages')+'/*.md'):
        page = Post(f,config)
        pages.append(page)
    return pages

def render_template(name, templates):
    pass

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

def update_pages(config, pages=None, templates=None):
    if pages is None:
        pass
    if templates is None:
        templates = load_templates(config)

    print("Generating pages")
    for p in pages:
        title = p.title
        html_content = p.get_html_content()
        page_content = templates['page'].render(title=title, html_content=html_content)
        raw_outname = p.slug + '/index.html'
        outname = config.outpathto(raw_outname)
        makedirs(os.path.dirname(outname))
        with open(outname, 'w') as f:
            f.write(page_content)

def update_posts_page(config,
        tpl_name,
        out_name,
        selector=lambda (pt,p): True,
        maxnum=0,
        extra_params={},
        posts=None, templates=None):
    if posts is None:
        posts = Posts(config)
    if templates is None:
        templates = load_templates(config)

    print("Generating from {}".format(tpl_name))
    filt_posts = [p for p in posts.posts if selector(p)]
    if maxnum > 0:
        filt_posts = utils.first_posts(filt_posts, maxnum)

    outfilename = config.outpathto(out_name)
    makedirs(os.path.dirname(outfilename))

    page_content = templates[tpl_name].render(posts=filt_posts, **extra_params)
    with open(config.outpathto(out_name), 'w') as f:
        f.write(page_content)


def update_index(config, posts=None, templates=None):
    page_size = config.getintdef('output', 'page_size', 10)
    print("Writing index")
    update_posts_page(config,
            'index',
            'index.html',
            maxnum=page_size,
            posts=posts, templates=templates)

def update_tag(config, tag, posts=None, templates=None):
    def match(ptp):
        (pt,p) = ptp
        if pt == 'blogpost' and tag in p.tags:
            return True
        elif pt == tag:
            return True
        return False

    print("Writing tag page " + tag)
    update_posts_page(config,
            'tag_archive',
            'tag/'+tag+'/index.html',
            match,
            extra_params={'tag': tag},
            posts=posts, templates=templates)

def update_feed(config, name, posts=None, templates=None):
    print("Updating Atom feed")
    update_posts_page(config,
            name+"_feed",
            'feed/'+name+'.xml',
            maxnum=20,
            posts=posts, templates=templates)

def update_dt_archive(config, year, month, posts=None, templates=None):
    def match(ptp):
        dt = get_dt(ptp)
        if dt.year == year and dt.month == month:
            return True
        return False

    print("Updating archive for {:02}/{}".format(month, year))
    update_posts_page(config,
            'dt_archive',
            '{}/{:02}/index.html'.format(year, month),
            match,
            extra_params={'month': month, 'year': year},
            posts=posts, templates=templates)

def update_all(config):
    makedirs(config.outpathto(''))

    update_assets(config)

    posts = Posts(config)
    templates = load_templates(config)

    print("Writing posts")
    for (ptype, post) in posts.posts:
        if ptype != 'blogpost': continue
        date_dir = config.outpathto(post.dt.strftime('%Y/%m'))
        post_dir = os.path.join(date_dir, post.slug)
        makedirs(post_dir)

        tpl_content = templates['blogpost_page'].render(post=post)
        html_fname = os.path.join(post_dir, 'index.html')
        with open(html_fname, 'w') as hf:
            hf.write(tpl_content)

    update_index(config, posts, templates)

    tags = posts.all_tags
    for t in tags:
        update_tag(config, t, posts, templates)

    # Atom feed
    update_feed(config, 'atom', posts, templates)
    htaccess_data = """<Files "atom.xml">
    ForceType application/atom+xml
</Files>
DirectoryIndex atom.xml
"""
    with open(config.outpathto('feed/.htaccess'), 'w') as f:
        f.write(htaccess_data)

    # Update date archive
    last_dt = datetime.datetime(1960,01,01)
    for pp in posts.posts:
        dt = get_dt(pp)
        if dt.month != last_dt.month or dt.year != last_dt.year:
            update_dt_archive(config, dt.year, dt.month, posts, templates)
        last_dt = dt

    # Pages
    pages = load_pages(config)
    update_pages(config, pages, templates)
