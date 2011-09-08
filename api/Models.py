from google.appengine.ext import db
from lib.embedly.client import Embedly

class DictModel(db.Model):
    def obj_to_dict(self):
        return dict([(p, unicode(getattr(self, p))) for p in self.properties()])

    def dict_to_obj(self, vals):
        for key, val in vals.items():
            setattr(self, key, val)


class Topic(db.Model):
    title = db.StringProperty()
    speaker = db.StringProperty()
    author = db.StringProperty()
    links = []

    def obj_to_dict(self):
        return dict([(p, unicode(getattr(self, p))) for p in self.properties()])

    def dict_to_obj(self, vals):
        for key, val in vals.items():
            setattr(self, key, val)

    """def __init__(self, **kwds):
        DictModel.__init__(self)
        self.links = []"""

    def add_link(self, linkDict):
        linkFromDB = Link.gql("WHERE url = :url", url=linkDict['url']).get()
        if not linkFromDB:
            link = Link()
        else:
            link = linkFromDB
            link.fetch = False
        link.unmarshal(linkDict)
        self.links.append(link)

    def unmarshal(self, jsonDict):
        linksDict = jsonDict['links']
        for linkDict in linksDict:
            self.add_link(linkDict)
        del jsonDict['links']
        self.dict_to_obj(jsonDict)

    def marshal(self):
        topicDict = self.obj_to_dict()
        topicDict['links'] = []
        topicDict['id'] = self.key().id()
        topicLinks = TopicLink.all()
        topicLinks.filter('topicId', self.key().id())
        for topicLink in topicLinks:
            link = Link.get_by_id(topicLink.linkId)
            if link:
                topicDict['links'].append(link.marshal())
        return topicDict

    def persist(self):
        #persist topic
        topicId = self.put().id()
        for link in self.links:
            #persist links
            if not link.fetch:
                linkId = link.key().id()
            else:
                linkId = link.persist().id()
            #persist relationship between topic and link
            if not TopicLink.gql("WHERE topicId=:topicId AND linkId=:linkId", topicId=topicId,
                                 linkId=linkId).get():
                topicLink = TopicLink()
                topicLink.topicId = topicId
                topicLink.linkId = linkId
                topicLink.put()


class Link(db.Model):
    url = db.LinkProperty()
    title = db.StringProperty()
    description = db.StringProperty()
    provider_name = db.StringProperty()
    thumbnail_url = db.LinkProperty()
    fetch = True

    def obj_to_dict(self):
        return dict([(p, unicode(getattr(self, p))) for p in self.properties()])

    def dict_to_obj(self, vals):
        for key, val in vals.items():
            setattr(self, key, val)

    """def __init__(self, **kwds):
        DictModel.__init__(self)
        self.fetch = True"""

    def persist(self):
        return self.put()

    def unmarshal(self, jsonDict):
        self.dict_to_obj(jsonDict)
        if self.fetch:
            embedlyLink = self.fetchFromEmbedly(self.url)
            self.title = embedlyLink.title
            self.description = embedlyLink.description
            self.provider_name = embedlyLink.provider_name
            self.thumbnail_url = embedlyLink.thumbnail_url

    def marshal(self):
        linkDict = self.obj_to_dict()
        linkDict['id'] = self.key().id()
        return linkDict

    def fetchFromEmbedly(self, url):
        client = Embedly('2ed57c50cffa11e0bc4a4040d3dc5c07')
        embedlyLink = client.oembed(url)
        return embedlyLink


class TopicLink(DictModel):
    topicId = db.IntegerProperty()
    linkId = db.IntegerProperty()

