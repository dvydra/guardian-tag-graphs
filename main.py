#!/usr/bin/env python
from django.utils import simplejson
from google.appengine.api import urlfetch
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from local_settings import API_KEY
import datetime
import logging
import os

API_URL = "http://content.guardianapis.com/search?tag=%s&from-date=%s&to-date=%s&format=json&show-tags=all&show-refinements=section&refinement-size=50&api-key=%s"


class MainHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write('Hello world!')

class RetrieveTagDataHander(webapp.RequestHandler):
    def get(self, tag):
        data = []
        for start_day, end_day, url in self.generate_url(tag):
            logging.info("%s to %s" % (start_day, end_day))
            data.append(
                (start_day, end_day, self.save_page(url),)
            )
        render(self.response, {'data': data}, 'index.html')

    def save_page(self, url):
        logging.info(url)
        content = simplejson.loads(urlfetch.fetch(url, deadline=10).content)

        try:
            r = ""
            refinements = content['response']['refinementGroups'][0]['refinements']
            for section in refinements:
                r += "%s: %d, " % (section['displayName'], section['count'])
        except KeyError:
            logging.error("no data for %s" % url)
        return r

    def generate_url(self, tag):
        for subtract_days in range(1,5):
            start_day = (datetime.date.today() - datetime.timedelta(weeks=subtract_days)).strftime("%Y-%m-%d")
            end_day   = (datetime.date.today() - datetime.timedelta(weeks=subtract_days-1, days=1)).strftime("%Y-%m-%d")
            #date_string = day.strftime("%Y-%m-%d")
            url = API_URL % (tag, start_day,end_day,API_KEY)
            yield start_day, end_day, url

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
