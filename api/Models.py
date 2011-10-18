from google.appengine.ext import db

class Link(db.Model):
    url = db.LinkProperty(required=True)
    title = db.StringProperty()
    description = db.StringProperty()
    provider_name = db.StringProperty()
    thumbnail_url = db.LinkProperty()
    created = db.DateProperty()

    def __str__(self):
        return self.url

class Topic(db.Model):
    title = db.StringProperty()
    speaker = db.StringProperty()
    author = db.StringProperty()
    topic_link = db.ReferenceProperty(Link, collection_name='topic')
    parentTopic = db.SelfReferenceProperty()
    created = db.DateProperty()

    def __str__(self):
        return self.title

class TopicMembership(db.Model):
    topic = db.ReferenceProperty(Topic, collection_name='link_memberships')
    link = db.ReferenceProperty(Link, collection_name='topic_memberships')

