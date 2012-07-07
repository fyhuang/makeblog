try:
    import configparser
except ImportError:
    import ConfigParser as configparser

import os.path
import collections

class Config(object):
    def __init__(self, filename, dirname, cp):
        self.cp = cp
        self.filename = filename
        self.dirname = dirname

        self.is_dynamic = False

        self.outputdir = os.path.normpath(os.path.join(self.dirname, cp.get('output', 'outputdir')))

    def get(self, section, key):
        return self.cp.get(section, key)

    def getdef(self, section, key, defaultval):
        try:
            return self.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return defaultval

    def getintdef(self, section, key, defaultval):
        return int(self.getdef(section, key, defaultval))

    def pathto(self, path):
        return os.path.join(self.dirname, path)

    def outpathto(self, path):
        result = os.path.join(self.outputdir, path)
        return result

    
    def get_user_options(self):
        res = collections.defaultdict(lambda: None)
        if not self.cp.has_section('user_options'):
            return res
        for (name, val) in self.cp.items('user_options'):
            res[name] = val
        return res

def load_config(filename):
    config_dir = os.path.dirname(os.path.abspath(filename))

    cp = configparser.SafeConfigParser()
    cp.read(filename)

    if not cp.get('output', 'wordpress_compat'):
        print("TODO: needs wordpress_compat")
        sys.exit(1)

    return Config(filename, config_dir, cp)
