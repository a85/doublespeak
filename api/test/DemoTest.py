import unittest
from google.appengine.ext import testbed
from google.appengine.ext import db
import DaoImpl

class TestModel(db.Model):
    """A model class used for testing."""
    number = db.IntegerProperty(default=42)
    text = db.StringProperty()


class DemoTestCase(unittest.TestCase):
    def setUp(self):
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()

    def tearDown(self):
        self.testbed.deactivate()


    def testCreateLinkFromUrl(self):
        link = DaoImpl.createLinkFromUrl("http://www.yahoo.com")

    def testGetLink(self):
        """create a link and get from the datastore and test
        """

    def testDeleteLink(self):
        """give a sample url and match the created embedly object.
        """

    def testDeleteNonExistentLink(self):
        """give a sample url and match the created embedly object.
        """

    def testUpdateLink(self):
        """test update of a link
        """

    def testCreateLinkFromUrl(self):
        """give a sample url and match the created embedly object.
        """
        self.assertEqual(0,1)

    def testCreateTopic(self):
        """simple create. without links.
        """
        topicDict = {'title': 'topTit', 'speaker': 'topSpeak', 'author': 'topAuth'}
        topic = DaoImpl.createTopic(topicDict)
        self.assertEqual(topic.title, 'topTit2')

    def testCreateTopicWithMissingAuthor(self):
        """throws exception
        """

    def testAddLinkToTopic(self):
        """add link to topic
        """

    def testGetTopic(self):
        """Check for added links and see accessible.
        """

    def testDeleteTopic(self):
        """ Check if links are also deleted or not.
        """

    def testDeleteLinkFromTopic(self):
        """delete link from topic
        """