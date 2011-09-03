from google.appengine.ext import db

class DictModel(db.Model):
    def obj_to_dict(self):
        return dict([(p, unicode(getattr(self, p))) for p in self.properties()])

    def dict_to_obj(self, vals):
        for key, val in vals.items():
            setattr(self, key, val)

class Topic(DictModel):
    title = db.StringProperty()
    speaker = db.StringProperty()
    author = db.StringProperty()

    def __init__(self):
        DictModel.__init__(self)
        self.links = []

    def unmarshal(self, jsonDict):
        linksDict = jsonDict['links']
        for linkDict in linksDict:
            link = Link()
            link.unmarshal(linkDict)
            self.links.append(link)
        del jsonDict['links']
        self.dict_to_obj(jsonDict)

    def marshal(self):
        return self.obj_to_dict()

    def addLink(self, link):
        return
    
    def persist(self):
        #persist topic
        self.put()
        #persist links
        for link in self.links:
            link.persist()


class Link(DictModel):
    title = db.StringProperty()
    description = db.StringProperty()
    url = db.LinkProperty()
    author_name = db.StringProperty()
    author_url = db.URLProperty()
    provider_name = db.StringProperty()
    provider_url = db.LinkProperty()
    thumbnail_url = db.LinkProperty()

    def persist(self):
        self.put()

    def unmarshal(self, jsonDict):
        self.dict_to_obj(jsonDict)

    def marshal(self):
        return self.obj_to_dict()