# Import a WordPress DB dump, outputting to the posts/ directory

# Currently imports:
#  * Posts (published)
#  * Draft posts
#  * Categories, tags (as tags)

# Supported formats (from phpMyAdmin):
#  * TODO: SQL (uncompressed)
#  * XML

# TODO: mynt compatibility

import os
import os.path
import sys
import re
import collections
from datetime import datetime

import xml.etree.ElementTree as xml

xtree = xml.parse(sys.argv[1])
xroot = xtree.getroot()

tags = {}
# Read categories, tags
terms_list = xroot.findall("wp_terms")
for t in terms_list:
    s_e = t.find('slug')
    i_e = t.find('term_id')
    tags[int(i_e.text)] = s_e.text


post_tags = collections.defaultdict(lambda: [])
# Read term relationships
term_rel_list = xroot.findall("wp_term_relationships")
for tr in term_rel_list:
    oid_e = tr.find('object_id')
    tid_e = tr.find('term_taxonomy_id')
    post_tags[int(oid_e.text)].append(int(tid_e.text))


url_nonchars_re = re.compile('[^\w\-&=]')
multiple_dashes_re = re.compile('-+')

# Read posts, write .md files
post_slugs = set()
post_list = xroot.findall("wp_posts")
for p in post_list:
    type_e = p.find('post_type')
    #if type_e.text == "revision" or type_e.text == "page":
    if type_e.text != "post":
        continue

    pid_e = p.find('ID')
    date_e = p.find('post_date')
    status_e = p.find('post_status')
    title_e = p.find('post_title')

    tag_names_list = [tags[t] for t in post_tags[int(pid_e.text)] if t in tags and tags[t] != 'uncategorized']
    tag_names = '[' + ', '.join(tag_names_list) + ']'

    header_block = '---\n' + \
            'title: "{}"\n'.format(title_e.text) + \
            'tags: {}\n'.format(tag_names) + \
            '---\n\n'
    #title_block = title_e.text + '\n' + ''.join('=' for i in range(len(title_e.text))) + '\n\n'

    slug = url_nonchars_re.sub('-', title_e.text).strip('-')
    slug = multiple_dashes_re.sub('-', slug).lower()

    dt = datetime.strptime(date_e.text, '%Y-%m-%d %H:%M:%S')
    post_fname = dt.strftime('%Y-%m-%d-%H-%M-') + slug + '.md'
    if status_e.text == "publish":
        # TODO: switch this on/off
        dt_dir = dt.strftime('%Y-%m')
        post_fname = "posts/" + dt_dir + '/' + post_fname
    else:
        post_fname = "drafts/" + post_fname
    if not os.path.exists(os.path.dirname(post_fname)):
        os.mkdir(os.path.dirname(post_fname))

    content_e = p.find('post_content')
    content_text = content_e.text
    if content_text is None:
        content_text = ""

    with open(post_fname, 'w') as f:
        f.write(header_block)
        #f.write(title_block)
        f.write(content_text)
        f.write('\n')
        print("Wrote post", title_e.text)
