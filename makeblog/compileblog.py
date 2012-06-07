import os
import os.path
import sys
import shutil
import datetime

from scss import Scss

from post import *
from blogdata import *
import utils
import twitter

def makedirs(d):
    try:
        os.makedirs(d)
    except os.error:
        pass

def compile_assets(config):
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

def compile_pages(blogdata):
    config = blogdata.config

    print("Generating pages")
    for p in blogdata.pages:
        title = p.title
        html_content = p.get_html_content()
        page_content = blogdata.templates['page'].render(title=title, html_content=html_content)
        raw_outname = p.slug + '/index.html'
        outname = config.outpathto(raw_outname)
        makedirs(os.path.dirname(outname))
        with open(outname, 'w') as f:
            f.write(page_content)

def compile_posts_page(blogdata,
        tpl_name,
        out_name,
        selector=lambda (pt,p): True,
        maxnum=0,
        extra_params={}):

    config = blogdata.config

    print("Generating from {}".format(tpl_name))
    filt_posts = [p for p in blogdata.posts if selector(p)]
    if maxnum > 0:
        filt_posts = utils.first_posts(filt_posts, maxnum)

    outfilename = config.outpathto(out_name)
    makedirs(os.path.dirname(outfilename))

    page_content = blogdata.templates[tpl_name].render(posts=filt_posts, **extra_params)
    with open(config.outpathto(out_name), 'w') as f:
        f.write(page_content)


def compile_index(blogdata):
    page_size = blogdata.config.getintdef('output', 'page_size', 10)
    print("Writing index")
    compile_posts_page(blogdata,
            'index',
            'index.html',
            maxnum=page_size)

def compile_tag(blogdata, tag):
    def match(ptp):
        (pt,p) = ptp
        if pt == 'blogpost' and tag in p.tags:
            return True
        elif pt == tag:
            return True
        return False

    print("Writing tag page " + tag)
    compile_posts_page(blogdata,
            'tag_archive',
            'tag/'+tag+'/index.html',
            match,
            extra_params={'tag': tag})

def compile_feed(blogdata, name):
    print("Updating Atom feed")
    compile_posts_page(blogdata,
            name+"_feed",
            'feed/'+name+'.xml',
            maxnum=20)

def compile_dt_archive(blogdata, year, month):
    def match(ptp):
        dt = get_dt(ptp)
        if dt.year == year and dt.month == month:
            return True
        return False

    print("Updating archive for {:02}/{}".format(month, year))
    compile_posts_page(blogdata,
            'dt_archive',
            '{}/{:02}/index.html'.format(year, month),
            match,
            extra_params={'month': month, 'year': year})

def compile_all(config):
    makedirs(config.outpathto(''))

    compile_assets(config)

    blogdata = Blogdata(config)

    print("Writing posts")
    for (ptype, post) in blogdata.posts:
        if ptype != 'blogpost': continue
        date_dir = config.outpathto(post.dt.strftime('%Y/%m'))
        post_dir = os.path.join(date_dir, post.slug)
        makedirs(post_dir)

        tpl_content = blogdata.templates['blogpost_page'].render(post=post)
        html_fname = os.path.join(post_dir, 'index.html')
        with open(html_fname, 'w') as hf:
            hf.write(tpl_content)

    compile_index(blogdata)

    tags = blogdata.all_tags
    for t in tags:
        compile_tag(blogdata, t)

    # Atom feed
    compile_feed(blogdata, 'atom')
    htaccess_data = """<Files "atom.xml">
    ForceType application/atom+xml
</Files>
DirectoryIndex atom.xml
"""
    with open(config.outpathto('feed/.htaccess'), 'w') as f:
        f.write(htaccess_data)

    # Update date archive
    for dt in blogdata.post_months:
        compile_dt_archive(blogdata, dt.year, dt.month)

    # Pages
    compile_pages(blogdata)
