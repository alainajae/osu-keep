import datetime
import flask
from google.cloud import datastore

app = flask.Flask(__name__)

def get_client():
    return datastore.Client('osu-keep')

def clean(s):
    """Return a string w/ angle brackets, endlines, & tab characters removed."""

    s = s.replace('<', '&lt;')
    s = s.replace('>', '&gt;')
    s = s.replace('\n', ' ')
    s = s.replace('\t', ' ')
    s = s.strip()
    if len(s) > 100:
        s = s[:100]

    return s


class Message():
    """An object representing a single chat message."""

    def __init__(self, user, text, time=None):
        """Initialize a message for named user."""

        self.user = user
        self.text = text

        if time:
            self.time = time
        else:
            self.time = datetime.datetime.now()


    def get_formatted_time(self):
        """Return this messages's time as a 'YYYYMMDD HH:MM:SS' string."""

        return self.time.strftime('%Y%m%d %H:%M:%S')


    def to_html(self):
        """Convert this message to an HTML div."""
        
        outputDiv = '<div class="Message">%s (%s): %s</div>'
        span = '<span class="%s">%s</span>'
        timeSpan = span % ('Time', self.get_formatted_time())
        userSpan = span % ('User', self.user)
        textSpan = span % ('Text', self.text)
        return outputDiv % (timeSpan, userSpan, textSpan)


    def __str__(self):
        """Return a simple formatted string with the message contents."""

        return '%s (%s): %s' % (self.get_formatted_time(), self.user, self.text)
    

    def __lt__(self, other):
        return self.time < other.time


    def __gt__(self, other):
        return self.time > other.time
    

    def __eq__(self, other):
        return self.time == other.time
    

    def __ne__(self, other):
        return self.time != other.time
    

    def __le__(self, other):
        return self.time <= other.time
    

    def __ge__(self, other):
        return self.time >= other.time


class ChatManager():
    """A class for managing chat messages."""

    def __init__(self):
        """Initialize the ChatManager with a new list of messages."""

        self.messages = []

    def get_client(self):
        return datastore.Client()

    def add_message(self, msg):
        """Add a message to our messages list."""

        self.messages.append(msg)        
        self.messages.sort()
        
    
    def create_cmt(self, user, text):
        """Create a new message with the current timestamp."""

        self.add_message(Message(clean(user), clean(text)))
        client = get_client()
        key = client.key('cmt')
        cmt = datastore.Entity(key)
        cmt['user'] = user
        cmt['text'] = text
        cmt['time'] = self.messages[-1].time
        client.put(cmt)
        return cmt


    def get_messages_html(self):
        """Return the current message contents as HTML."""

        result = ''
        for msg in self.messages:
            result += msg.to_html()
            result += '\n'
        return result

    
    def get_cmts(self):
        result = []
        client = get_client()
        query = client.query(kind='cmt')
        for entity in query.fetch():
            result.append(entity)
        return result

