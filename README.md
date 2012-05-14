makeblog
========

*Note: `makeblog` is still very alpha-quality software. Social media integration and commenting on posts are *not* yet implemented.*

`makeblog` is a social media-aware static blog generator. It creates a set of HTML blog pages based on Markdown-formatted post files and a configurable set of your recent social media posts.

Compare `makeblog` to traditional PHP-based blog software. `makeblog`'s advantages:

* Runs faster (mostly just HTML pages)
* Less stuff to maintain, especially for small blogs
* Easy to write themes
* Store your blog posts in version control!

On the other hand, you would be better off with a different blog platform if your blog:

* Gets a lot of comments (`makeblog` is still not very efficient at handling comments)

To make your transition even easier, `makeblog` includes a script to import your existing WordPress blog posts--just dump your SQL database into an XML file (using phpMyAdmin) and run the script!

Special Directories
===================

* `posts`: holds your MD-formatted blog posts
* `assets`: holds static assets, copied directly over to final site, except for .scss files which are compiled to CSS first.


Changelog
=========

~~~
Version 0.3 (planned):
    * Commenting
    * Almost-static -- update pages on command, etc.

Version 0.2 (planned):
	* More commands--auto generate new blog, etc.
	* Archive by date
	* RSS feeds
    * DONE new post command
	* DONE Twitter integration
	* DONE Fix WP import bugs (tags)

Version 0.1 (2012/5/10):
	* WordPress import working
	* Basic HTML blog generation working
~~~
