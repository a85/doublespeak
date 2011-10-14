import logging
from google.appengine.api.datastore_errors import TransactionFailedError
from google.appengine.ext.db import NotSavedError
from Models import *
from Exceptions import *
from Util import *

def createLinkFromUrl(url, parent=None):
    link = createEmbedlyLinkFromUrl(url, parent)
    return createLinkFromObj(link)


def createLinkFromDict(linkDict, parent=None):
    """
    Create Link from dict entries
    Raises:
      URLNotFoundException: If URL missing from dict.
    """

    if 'url' not in linkDict:
        raise URLNotFoundException

    link = createEmbedlyLinkFromUrl(linkDict['url'], parent)

    if 'title' in linkDict:
        link.title = linkDict['title']
    if 'description' in linkDict:
        link.description = linkDict['description']
    if 'provider_name' in linkDict:
        link.provider_name = linkDict['provider_name']
    if 'thumbnail_url' in linkDict:
        link.thumbnail_url = linkDict['thumbnail_url']
    return createLinkFromObj(link)


def createLinkFromObj(link):
    """Create link entry in the datastore"""
    try:
        link.put()
    except TransactionFailedError, e:
        logging.error('Transaction failed for link :1 on datastore', link.url)
        raise TransactionFailedError("Link transaction failed on datastore." + e.__str__())
    return link


def getLink(linkId):
    """Get link from datastore"""
    return Link.get_by_id(int(linkId))


def deleteLink(linkId):
    """Delete link from datastore. Check if link present under any topics. If yes throw exception otherwise go ahead.
    Use cross-cutting feature of many-many relationships in the Oreilly book.
    """
    link = getLink(linkId)
    if link.topic_membership != None:
        raise LinkUnderTopicException
    try:
        link.delete()
    except NotSavedError:
        logging.error('Failed to delete link :1 from datastore', link.key().id())
        return False
    return True


def updateLink(linkId, linkDict, parent):
    """
    Update the linkId with the link details.

    Args:
      linkId: datastore ID of the link
      linkDict: dictionary of updates in the link.

    Returns:
      Updated link object. None if failure.

    Raises:
      URLModifiedException: If URL for this link is changed.
    """
    if parent is not None:
        link = Link.get_by_id(int(linkId), parent)
    else:
        link = Link.get_by_id(int(linkId))
    if 'url' in linkDict and link.url != linkDict['url']:
        raise URLModifiedException
    if 'title' in linkDict:
        link.title = linkDict['title']
    if 'description' in linkDict:
        link.description = linkDict['description']
    if 'provider_name' in linkDict:
        link.provider_name = linkDict['provider_name']
    if 'thumbnail_url' in linkDict:
        link.thumbnail_url = linkDict['thumbnail_url']
    return createLinkFromObj(link)


def createTopic(topicDict):
    """Create topic with given details.
    """
    if 'title' not in topicDict:
        raise TitleNotFoundException
    if 'speaker' not in topicDict:
        raise SpeakerNotFoundException
    if 'author' not in topicDict:
        raise AuthorNotFoundException

    #logging.debug("Creating topic: :1", simplejson.dumps(topicDict))

    try:
        topic = db.run_in_transaction(__create_topic_txn, topicDict=topicDict)
    except TransactionFailedError, e:
        logging.error('Failed to create an entry for topic on datastore. Exception :1', e)
        raise TransactionFailedError("Topic Transaction failed on datastore" + e.__str__())

    return topic


def __create_topic_txn(topicDict):
    linksDict = topicDict['links']
    del topicDict['links']

    topic = Topic()
    topic.title = topicDict['title']
    topic.speaker = topicDict['speaker']
    topic.author = topicDict['author']
    topic.put()
    topic_link = createLinkFromUrl(topicDict['topic_link'], topic)
    topic.topic_link = topic_link
    topic.put()
    for linkDict in linksDict:
        link = createLinkFromDict(linkDict, topic)
        addLinkToTopic(topic, link)
    return topic


def getTopics():
    return [topic for topic in Topic.all()]


def getTopic(topicId):
    """Get Topic from datastore
    """
    return Topic.get_by_id(int(topicId))


def updateTopic(topicId, topicDict):
    """Update topic in datastore.
    """
    topic = getTopic(topicId)
    try:
        topic = db.run_in_transaction(__update_topic_txn, topic=topic, topicDict=topicDict)
    except TransactionFailedError, e:
        logging.error('Failed to update entry for topic :1 on datastore. Exception :2', topic.key().id().e)
        raise TransactionFailedError("Topic Transaction failed on datastore." + e.__str__())
    return topic


def __update_topic_txn(topic, topicDict):
    linksDict = topicDict['links']
    del topicDict['links']

    if 'title' in topicDict:
        topic.title = topicDict['title']
    if 'speaker' in topicDict:
        topic.speaker = topicDict['speaker']
    if 'author' in topicDict:
        topic.author = topicDict['author']

    topic.put()
    for linkDict in linksDict:
        if 'id' not in linkDict:
            link = createLinkFromDict(linkDict, topic)
            addLinkToTopic(topic, link)
        else:
            updateLink(linkDict['id'], linkDict, topic)
    return topic


def deleteTopic(topicId):
    """Check all links, if any of them not referring from any other topics, delete maadi.
    """
    topic = getTopic(topicId)
    for tm in topic.link_memberships: #Delete link memberships.
        try:
            tm.delete()
        except NotSavedError:
            logging.error('Failed to delete membership of link :1 from topic :2', tm.link.key().id(), topic.key().id())
        deleteLink(tm.link.key().id())
    try:
        topic.delete()
    except NotSavedError:
        logging.error('Failed to delete topic :2', topicId)
        return False
    return True


def addLinkToTopic(topic, link):
    """add link to topic
    """
    tm = TopicMembership(topic=topic, link=link, parent=topic)
    try:
        tm.put()
    except TransactionFailedError, e:
        logging.error('Failed to create a membership entry for link ":1" for topic ":2" on datastore', link.key().id(),
                      topic.key().id())
        raise TransactionFailedError("Topic Membership Transaction failed on datastore" + e.__str__())
    return tm


def deleteLinkFromTopic(topic, link):
    """delete link from topic.
    """
    for tm in topic.link_memberships:
        if tm.link == link:
            try:
                tm.delete()
            except NotSavedError:
                logging.error('Failed to delete membership of link :1 from topic :2', link.key().id(), topic.key().id())
                return False
            deleteLink(link.key().id())
            break

    return True


def getLinks(topic_id):
    topic = getTopic(topic_id)
    if topic:
        return [tm.link for tm in topic.link_memberships]
    else:
        raise TopicNotFoundException