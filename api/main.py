#DoubleSpeakMain will change your life
from django.utils import simplejson

from google.appengine.ext.webapp import util

import os
import Models
import DaoImpl
import Util
from Exceptions import TopicNotFoundException

import fix_path, keyStore
from tornado import wsgi, web
from lib import oauth

def error(msg):
    err = dict()
    err['message'] = msg
    return simplejson.dumps(err)


class TopicsHandler(web.RequestHandler):
    def get(self): #done
        topics = DaoImpl.getTopics()
        topicsDict = []
        for topic in topics:
            topicDict = Util.topicToDict(topic)
            if topicDict:
                topicsDict.append(topicDict)
        self.set_status(200)
        self.write(simplejson.dumps(topicsDict))
        self.set_header("Content-Type", "application/json")

    def post(self): #done
        if self.request.body:
            topicDict = simplejson.loads(self.request.body)
            try:
                topic = DaoImpl.createTopic(topicDict)
                self.set_status(200)
                self.write(simplejson.dumps(Util.topicToDict(topic)))
            except Exception, e:
                self.set_status(400)
                self.write(error(e.__str__()))
        else:
            self.set_status(400)
            self.write(error("Empty post body."))
        self.set_header("Content-Type", "application/json")


class TopicHandler(web.RequestHandler):
    def get(self, topic_id): #done
        topic = DaoImpl.getTopic(topic_id)

        if topic:
            topicDict = Util.topicToDict(topic)
            self.set_status(200)
            self.write(simplejson.dumps(topicDict))
        else:
            self.set_status(404)
            self.write(simplejson.dumps(error('Topic not found.')))

        self.set_header("Content-Type", "application/json")

    def put(self, topic_id):
        if self.request.body:
            topicDict = simplejson.loads(self.request.body)
            try:
                topic = DaoImpl.updateTopic(topic_id, topicDict)
                self.set_status(200)
                self.write(simplejson.dumps(Util.topicToDict(topic)))
            except Exception, e:
                self.set_status(400)
                self.write(error(e.__str__()))
        else:
            self.set_status(400)
            self.write(error("Empty body."))
        self.set_header("Content-Type", "application/json")


class TopicLinksHandler(web.RequestHandler):
    def get(self, topic_id): #done
        try:
            links = DaoImpl.getLinks(topic_id)
            linksDict = [Util.linkToDict(link) for link in links]
            self.set_status(200)
            self.write(simplejson.dumps(linksDict))
        except TopicNotFoundException, e:
            self.set_status(404)
            self.write(error(e.__str__())) #figure how to write exception text.
        self.set_header("Content-Type", "application/json")


    def post(self, topic_id):#done
        if self.request.body:
            linkDict = simplejson.loads(self.request.body)
            try:
                topic = DaoImpl.getTopic(topic_id)
                if not topic:
                    raise TopicNotFoundException
                link = DaoImpl.createLinkFromDict(linkDict, topic)
                DaoImpl.addLinkToTopic(topic, link)
                self.set_status(200)
                self.write(simplejson.dumps(Util.linkToDict(link)))
            except Exception, e:
                self.set_status(400)
                self.write(error(e.__str__()))
        else:
            self.set_status(400)
            self.write(error("Empty body."))
        self.set_header("Content-Type", "application/json")


class TopicLinkHandler(web.RequestHandler):
    def get(self, topic_id, link_id):
        link = DaoImpl.getLink(link_id)
        if link:
            linkDict = Util.linkToDict(link)
            self.set_status(200)
            self.write(simplejson.dumps(linkDict))
        else:
            self.set_status(404)
            self.write(simplejson.dumps(error('Link not found.')))
        self.set_header("Content-Type", "application/json")


    def put(self, link_id): #vote up/down information will be stored in the TopicLink table.
        if self.request.body:
            linkDict = simplejson.loads(self.request.body)
            try:
                link = DaoImpl.updateLink(link_id, linkDict, None)
                self.set_status(200)
                self.write(simplejson.dumps(Util.linkToDict(link)))
            except Exception, e:
                self.set_status(400)
                self.write(error(e.__str__()))
        else:
            self.set_status(400)
            self.write(error("Empty body."))
        self.set_header("Content-Type", "application/json")


class TestTwitterHandler(web.RequestHandler):
    def get(self):
        consumer_key = keyStore.__oauthConsumerKey__
        consumer_secret = keyStore.__oauthConsumerSecret__
        callback_url = "http://localhost:9999/callback"

        client = oauth.TwitterClient(consumer_key, consumer_secret, callback_url)

        self.redirect(client.get_authorization_url())


class CallbackHandler(web.RequestHandler):
    def get(self):
        consumer_key = keyStore.__oauthConsumerKey__
        consumer_secret = keyStore.__oauthConsumerSecret__
        callback_url = "http://localhost:9999/callback"
        client = oauth.TwitterClient(consumer_key, consumer_secret, callback_url)
        auth_token = self.get_argument("oauth_token")
        auth_verifier = self.get_argument("oauth_verifier")
        user_info = client.get_user_info(auth_token, auth_verifier=auth_verifier)
        user_info


settings = {
    "page_title": u"doubleSpeak",
    "template_path": os.path.join(os.path.dirname(__file__), "templates"),
    "sourcecode_stylesheet": "default",
    "xsrf_cookies": False,
    }

handlers = [
    (r"/api/topics", TopicsHandler),
    (r"/api/topics/(\d+)", TopicHandler),
    (r"/api/topics/(\d+)/links", TopicLinksHandler),
    (r"/api/topics/(\d+)/links/(\d+)", TopicLinkHandler),
    (r"/testTwitter", TestTwitterHandler),
    (r"/callback", CallbackHandler),
]

def main():
    application = wsgi.WSGIApplication(handlers, **settings)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()