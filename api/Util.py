import keyStore
from NewModel import Link
from lib.embedly.client import Embedly
from google.appengine.ext import db

def createEmbedlyLinkFromUrl(url, parent):
    """use Embedly to retrieve link information and create link Obj."""
    embClient = Embedly(keyStore.__embedly__)
    embObj = embClient.oembed(url)
    if parent is None:
        link = Link(url=url)
    else:
        link = Link(url=url, parent=parent)
    link.title = embObj.title
    link.description = embObj.description[:499]
    link.provider_name = embObj.provider_name
    link.thumbnail_url = embObj.thumbnail_url
    return link


def obj_to_dict(obj):
    objDict = dict()
    for p in obj.properties():
        element = getattr(obj, p)
        if isinstance(element, db.Model):
            objDict[p] = unicode(element.key().id())
        else:
            objDict[p] = unicode(element)
        #return dict([(p, unicode(getattr(self, p))) for p in self.properties()])
    return objDict


def linkToDict(link):
    linkDict = obj_to_dict(link)
    linkDict['id'] = link.key().id()
    return linkDict


def topicToDict(topic):
    topicDict = obj_to_dict(topic)
    linksList = []
    for tm in topic.link_memberships:
        linksList.append(linkToDict(tm.link))
    topicDict['links'] = linksList
    topicDict['id'] = topic.key().id()
    return topicDict