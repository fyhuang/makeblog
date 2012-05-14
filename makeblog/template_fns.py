# Functions used inside templates

def template_get_asset(config):
    def tga(url):
        return config.get('output', 'prefix').rstrip('/') + '/assets/' + url.lstrip('/')
    return tga

def template_get_url(config):
    def tgu(url):
        return config.get('output', 'prefix').rstrip('/') + '/' + url.lstrip('/')
    return tgu

def template_ptype_template(templates):
    def ptt(ptype):
        return templates[ptype]
    return ptt

def template_pretty_date(dt):
    return dt.strftime("%Y/%m/%d")
