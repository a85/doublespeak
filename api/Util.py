from google.appengine.ext import db
import Models
from lib.embedly.client import Embedly

def dict_to_obj(cls, vals):
    obj = cls()
    for key, val in vals.items():
        setattr(obj, key, val)
    return obj


def obj_to_dict(obj):
    return dict([(p, unicode(getattr(obj, p))) for p in obj.properties()])


def dict_to_existing_obj(obj, vals):
    for key, val in vals.items():
        setattr(obj, key, val)
    return obj


def getEmbedlyObj(url):
    client = Embedly('2ed57c50cffa11e0bc4a4040d3dc5c07')
    embedlyObj = client.oembed(url)
    return embedlyObj

# generate LinkObj for given URL
def getLinkObj(url, topic_id):
    #check if obj can be generated from DB. If not generate Embedly Obj.
    embedlyObj = getEmbedlyObj(url)
    linkObj = Models.Link(parent=genKey(topic_id), id=1, title=embedlyObj.title, description=embedlyObj.description,
                       url=url)
    return linkObj


def genKey(name=None):
    return db.Key.from_path(name or 'default')