from HTMLParser import HTMLParser


class HtmlFileParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.crdate = ''

    def handle_starttag(self, tag, attributes):
           
        if tag != 'p': return
        attributes = dict(attributes)
        if 'id' in attributes:
            if attributes['id'] == 'crdate':
                # extract the name attribute of the p tag of id == 'crdate'
                self.crdate = attributes.get('name', None)
                return

    def handle_data(self, data):
        pass


def getDateFromHtml(hpath):
    p = HtmlFileParser()
    f = open(hpath)
    html = f.read()
    p.feed(html)
    p.close()
    return p.crdate


