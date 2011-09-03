#DoubleSpeakMain will change your life
from django.utils import simplejson

from google.appengine.ext.webapp import util

import os
import Models

import fix_path
from tornado import wsgi, web

class TopicsHandler(web.RequestHandler):
    def get(self):
        topics = Models.Topic.all()
        for topic in topics:
            topicDict = topic.marshal()

    def post(self):
        if(self.request.body):
            topic = Models.Topic()
            topic.unmarshal(simplejson.loads(self.request.body))
            topic.persist()

settings = {
    "page_title": u"doubleSpeak",
    "template_path": os.path.join(os.path.dirname(__file__), "templates"),
    "sourcecode_stylesheet": "default",
    "xsrf_cookies": False,
    }

handlers = [
    (r"/topics", TopicsHandler),
    #(r"/topics/(\d+)", TopicHandler),
    #(r"/topics/(\d+)/links", TopicLinksHandler),
    #(r"/topics/(\d+)/links/(\d+)", TopicLinkHandler),
]

def main():
    application = wsgi.WSGIApplication(handlers, **settings)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()