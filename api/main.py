import os
from django.utils import simplejson
from google.appengine.api.datastore_errors import TransactionFailedError
from google.appengine.ext import db
from google.appengine.ext.webapp import util
import Util

import fix_path
import Models

from tornado import web
from tornado import wsgi
from lib.embedly import Embedly

class MainHandler(web.RequestHandler):
    def get(self):
        client = Embedly('2ed57c50cffa11e0bc4a4040d3dc5c07')
        obj = client.oembed('http://instagr.am/p/BL7ti/')
        self.set_header("Content-Type", "application/json")
        returnObj = {};
        returnObj['type'] = obj.type
        returnObj['title'] = obj.title
        returnObj['provider_name'] = obj.provider_name
        return self.write(simplejson.dumps(returnObj))


def generateError(error):
    return simplejson.dumps({'error': error})


class TopicsHandler(web.RequestHandler):
    def get(self):
        topics = Models.Topic.all()
        topicsList = []
        for topic in topics:
            topicsList.append(Util.obj_to_dict(topic))
        self.set_header("Content-Type", "application/json")
        self.write(simplejson.dumps(topicsList))

    def post(self):
        if self.request.body:
            topic = Models.Topic(simplejson.loads(self.request.body))
        else:
            generateError('The request cannot be empty.')
            return
        try:
            topic.put()
        except TransactionFailedError:
            generateError('Failed to commit.')


class TopicHandler(web.RequestHandler):
    def get(self, topic_id):
        topic = Models.Topic.get_by_id(int(topic_id))
        links = Models.MapTopicLink.gql("WHERE topic = :1", int(topic_id))
        ct = Models.CompositeTopic(topic)
        ct.fillLinks(links)
        self.write(simplejson.dumps(ct.compositeTopic))


    def put(self, topic_id):
        topic = Models.Topic.get_by_id(int(topic_id))
        if self.request.body:
            Util.dict_to_existing_obj(topic, simplejson.loads(self.request.body))
        else:
            generateError('The request cannot be empty.')
            return
        try:
            topic.put()
        except TransactionFailedError:
            generateError('Failed to commit.')


class TopicLinksHandler(web.RequestHandler):
    def get(self, topic_id):
        links = Models.Link.all()
        links.ancestor(Util.genKey(topic_id))
        linksList = []
        for link in links:
            linksList.append(Util.obj_to_dict(link))
        self.set_header("Content-Type", "application/json")
        self.write(simplejson.dumps(linksList))

    def post(self, topic_id):
        if self.get_argument('url'):
            url = self.get_argument('url')
            link = Util.getLinkObj(url, topic_id)
        else:
            generateError('Provide url')
            return
        try:
            key = link.put()
            self.write(key.id())
        except TransactionFailedError:
            generateError('Failed to commit.')


class TopicLinkHandler(web.RequestHandler):
    def get(self, link_id):
        return        

settings = {
    "page_title": u"doubleSpeak",
    "template_path": os.path.join(os.path.dirname(__file__), "templates"),
    "sourcecode_stylesheet": "default",
    "xsrf_cookies": False,
    }

handlers = [
    (r"/topics", TopicsHandler),
    (r"/topics/(\d+)", TopicHandler),
    (r"/topics/(\d+)/links", TopicLinksHandler),
    (r"/topics/(\d+)/links/(\d+)", TopicLinkHandler),
]

def main():
    application = wsgi.WSGIApplication(handlers, **settings)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
