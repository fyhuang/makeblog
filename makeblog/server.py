import sys
import errno
import datetime
import os.path

import yaml
from flask import Flask, send_file, redirect, abort, request

import compileblog
import blogdata as _bd
import template_fns


def post_comment(blogdata, slug, comment):
    with blogdata.comment_lock:
        comments_file = blogdata.config.pathto(_bd.COMMENTS_FILENAME)
        """if not os.path.exists(comments_file):
            comments = []
        else:
            with open(comments_file) as f:
                comments = yaml.load(f.read())"""

        comment['slug'] = slug
        comment['dt'] = datetime.datetime.now()
        #comments.append(comment)

        # Take advantage of structured YAML format
        with open(comments_file, 'a') as f:
            f.write(yaml.dump([comment]))

    # Recompile that page
    compileblog.compile_post(blogdata, slug)


app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def blog_page(path):
    bd = app.config['bd']
    print("Got path " + path)
    destpath = bd.config.outpathto(path)
    if destpath[-1] == '/':
        destpath += 'index.html'
    try:
        return send_file(destpath)
    except IOError as e:
        if e.errno == errno.ENOENT:
            abort(404)
        elif e.errno == errno.EISDIR: # "Is a directory"
            tgu = template_fns.template_get_url(bd.config)
            return redirect(tgu(path + '/'))

@app.route('/post_comment', methods=['POST'])
def post_comment_action():
    bd = app.config['bd']
    slug = request.args.get('slug', '')
    comment = {
            'text': request.form['comment_text'],
            'author': request.form['comment_author'],
            'aurl': request.form['comment_aurl'],
            }
    post_comment(bd, request.args.get('slug', ''), comment)

    tgu = template_fns.template_get_url(bd.config)
    return redirect(tgu('/'+bd.posts_by_slug[slug].get_url()))

def serve(config):
    if not config.is_dynamic:
        print("ERROR: config must be dynamic in order to serve")
        sys.exit(1)
    blogdata = _bd.Blogdata(config)

    # Recompile for dynamic
    print("Recompiling blog")
    compileblog.compile_all(config)

    app.config['bd'] = blogdata
    app.run(debug=True)
