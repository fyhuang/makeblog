from setuptools import setup

setup(name='makeblog',
      version='0.1',
      description='Social media-aware static blog generator',
      author='Yifeng Huang',
      author_email='me@nongraphical.com',
      url='https://github.com/fyhuang/makeblog',

      packages=['makeblog'],
      entry_points={
          'console_scripts': [
              'makeblog = makeblog.makeblog:main',
              ],
          },

      install_requires=['jinja2', 'Markdown', 'PyYAML', 'pyScss', 'requests'],
      )
