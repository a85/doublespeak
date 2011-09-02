from google.appengine.ext import db

class DictModel(db.Model):
    def obj_to_dict(self):
        return dict([(p, unicode(getattr(self, p))) for p in self.properties()])

    def dict_to_obj(self, vals):
        for key, val in vals.items():
            setattr(self, key, val)


class Link(db.Model):
    title = db.StringProperty()
    description = db.StringProperty()
    url = db.LinkProperty()
    author_name = db.StringProperty()
    author_url = db.URLProperty()
    provider_name = db.StringProperty()
    provider_url = db.LinkProperty()
    thumbnail_url = db.LinkProperty()


class Topic(DictModel):
    title = db.StringProperty()
    speaker = db.StringProperty()
    author = db.StringProperty()

    def __init__(self, jsonDict):
        DictModel.__init__(self)
        self.dict_to_obj(jsonDict)


class MapTopicLink(db.Model):
    topic = db.IntegerProperty
    link = db.IntegerProperty


class CompositeTopic():
    def __init__(self, topicDB):
        self.compositeTopic = topicDB.to_dict

    def fillLinks(self, linksDB):
        links = []
        for linkDB in linksDB:
            links.append(linkDB.to_dict())
        self.compositeTopic['links'] = links
