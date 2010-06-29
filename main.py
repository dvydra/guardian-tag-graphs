#!/usr/bin/env python
from django.utils import simplejson
from google.appengine.api import urlfetch
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from local_settings import API_KEY
import datetime
import logging

API_URL = "http://content.guardianapis.com/search?tag=%s&from-date=%s&to-date=%s&format=json&show-tags=all&show-refinements=keyword&refinement-size=50&api-key=%s"


class MainHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write('Hello world!')

class RetrieveTagDataHander(webapp.RequestHandler):
    def get(self, tag):
        for date_string, url in self.generate_url(tag):
            self.save_page(url, date_string)

    def save_page(self, url, date_string):
        content = simplejson.loads(urlfetch.fetch(url).content)
        logging.info(date_string)
        r = "<h1>%s</h1>" % date_string
        try:
            refinements = content['response']['refinementGroups'][0]['refinements']
            r += "<p>"
            for section in refinements:
                r += "%s: %d, " % (section['displayName'], section['count'])
            r += "</p>"
        except KeyError:
            logging.error("no data for %s" % url)
            r += "<p><b>No data for %s</b></p>" % date_string
        r += "<hr />"
        self.response.out.write(r)

    def generate_url(self, tag):
        for subtract_days in range(0,30):
            day = datetime.date.today() - datetime.timedelta(days=subtract_days)
            date_string = day.strftime("%Y-%m-%d")
            url = API_URL % (tag, date_string,date_string,API_KEY)
            yield date_string, url

def render(response, context, template_path):
    path = os.path.join(os.path.dirname(__file__), template_path)
    response.out.write(template.render(path, context))

def main():
    application = webapp.WSGIApplication([
        ('/', MainHandler),
        ('/data/(.*)', RetrieveTagDataHander),

    ],debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
