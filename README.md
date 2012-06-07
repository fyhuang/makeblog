makeblog
========

*Note: `makeblog` is still very alpha-quality software. Most social media integration and commenting on posts are *not* yet implemented.*

`makeblog` is a social media-aware static blog generator. It creates a set of HTML blog pages based on Markdown-formatted post files and a configurable set of your recent social media posts.

Compare `makeblog` to traditional PHP-based blog software. `makeblog`'s advantages:

* Runs faster (mostly just HTML pages)
* Less stuff to maintain, especially for small blogs
* Easy to write themes
* Store your blog posts in version control!

On the other hand, you would be better off with a different blog platform if your blog:

* Gets a lot of comments (`makeblog` is still not very efficient at handling comments)

To make your transition even easier, `makeblog` includes a script to import your existing WordPress blog posts--just dump your SQL database into an XML file (using phpMyAdmin) and run the script!

Quickstart Guide
================

1. Install `makeblog` (run `python setup.py install` in a virtualenv)
2. Create a directory to hold your blog. Optionally add it to version control. (TODO: automatic command for this.)
3. Add posts to the `posts/` directory.
4. Create a configuration file (see `sample-config.ini`)
5. Compile your blog with `makeblog compile [config.ini]`
6. And you're done!


Special Directories
===================

* `posts`: holds your MD-formatted blog posts
* `assets`: holds static assets, copied directly over to final site, except for .scss files which are compiled to CSS first.
* `templates`: holds Jinja2-format templates



Changelog
=========

~~~
Version 0.4 (planned):
    * Commenting
    * WP import comments
    * Almost-static -- update pages on command, etc.
    * Pingbacks

Version 0.3 (planned):
    * Tutorial on how to use makeblog
    * Clean up config file structure
    * Friendlier user-interface
    * Make editor configurable
    * Generate new blog command
	* Edit blog post command
    * Sitemaps (for Google)

Version 0.2 (2012/5/25):
	* Archive by date
	* RSS feeds
    * New post command
	* Twitter integration
	* Fix WP import bugs (tags)

Version 0.1 (2012/5/10):
	* WordPress import working
	* Basic HTML blog generation working
~~~
