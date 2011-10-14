__author__ = 'asobti'

"""Exceptions in doublespeak"""

class URLModifiedException(Exception):
    """Exception if URL is modified in a link."""
    def __str__(self):
        return "URL modified in the link"


class URLNotFoundException(Exception):
    """Exception if URL not given."""
    def __str__(self):
        return "URL not given"


class TitleNotFoundException(Exception):
    """Exception if title not given."""
    def __str__(self):
        return "Title not given"


class SpeakerNotFoundException(Exception):
    """Exception if speaker not given."""
    def __str__(self):
        return "Speaker not given"


class AuthorNotFoundException(Exception):
    """Exception if author not given."""
    def __str__(self):
        return "Author not given"


class LinkUnderTopicException(Exception):
    """Exception if link being deleted is used by a topic."""
    def __str__(self):
        return "Link is being used by topic"


class TopicNotFoundException(Exception):
    """Exception if topic not present in datastore."""
    def __str__(self):
        return "Topic not found in datastore"

class TopicNotFoundException(Exception):
    """Exception if topic not present in datastore."""
    def __str__(self):
        return "Topic not found in datastore"
