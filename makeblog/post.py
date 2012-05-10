import os.path
from datetime import datetime

import yaml

from markdown import markdown

def count_chars(content, num):
    so_far = 0
    in_tag = False
    for i,c in enumerate(content):
        if c == '<':
            in_tag = True
        elif c == '>':
            in_tag = False
            continue

        if not in_tag:
            so_far += 1
        if so_far >= num:
            return i
    return len(content)-1

class Post(object):
    def __init__(self, fname, config):
        self.config = config
        self.fname = fname
        bname = os.path.basename(fname)
        # TODO
        dt_str = bname[:16]
        self.slug = bname[17:-3]

        # Read the YAML header
        self.read_header()

        self.title = self.meta['title']
        self.tags = []
        if 'tags' in self.meta:
            self.tags = self.meta['tags']

        self.dt = datetime.strptime(dt_str, '%Y-%m-%d-%H-%M')

    def read_header(self):
        in_header = False
        header_lines = []
        with open(self.fname, 'r') as f:
            for line in f:
                if line == '---\n':
                    in_header = not in_header
                    if not in_header:
                        break
                    continue
                if in_header:
                    header_lines.append(line)
        self.meta = yaml.load(''.join(header_lines))

    def get_pretty_date(self):
        day_fmt = str(self.dt.strftime('%d')).lstrip('0')
        if len(day_fmt) == 2 and day_fmt[-2] == '1':
            day_fmt += 'th'
        else:
            if day_fmt[-1] == '1':
                day_fmt += 'st'
            elif day_fmt[-1] == '2':
                day_fmt += 'nd'
            elif day_fmt[-1] == '3':
                day_fmt += 'rd'
            else:
                day_fmt += 'th'

        return '{} {}, {}'.format(self.dt.strftime('%B'), day_fmt, self.dt.strftime('%Y'))

    def get_url(self):
        return self.dt.strftime('%Y/%m/') + self.slug + '/'

    def get_content(self):
        with open(self.fname, 'r') as f:
            lines = f.readlines()
            ix = lines.index('---\n')
            ix2 = lines.index('---\n', ix+1)
            return ''.join(lines[ix2+1:])

    def md(self, text):
        md_result = markdown(text, output_format='html5', extensions=['fenced_code', 'headerid'])
        # TODO: replace links
        return md_result

    def get_html_content(self):
        return self.md(self.get_content())

    def get_html_excerpt(self):
        num_chars = self.config.getdef('output', 'excerpt_chars', 600) # TODO

        content = self.get_content()
        ix = content.find('<!--more-->')
        if ix != -1:
            return self.md(content[:ix])
        else:
            cix = count_chars(content, num_chars)
            if len(content)-1 != cix and content[cix] != '\n':
                pix = content[:cix].rfind('\n\n')
                if pix != -1:
                    return self.md(content[:pix])
            return self.md(content[:cix])

def load_all_posts(config):
    posts = []
    for (dirpath, dirnames, filenames) in os.walk(config.pathto('posts')):
        for f in filenames:
            post = Post(os.path.join(dirpath, f), config)
            posts.append(post)
    posts.sort(key=lambda p: p.dt, reverse=True)
    return posts
