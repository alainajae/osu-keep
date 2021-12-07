import datetime
from google.cloud import datastore

def get_client():
    return datastore.Client('osu-keep')


def ds_create_comment():
    client = get_client()
    # Calling key without an ID will generate (an int) one for you.
    key = client.key('comment')
    return datastore.Entity(key)

def ds_get_comments(rev=True):
    """Query datastore for comments and return an array of type Comment"""
    result = []
    client = get_client()
    query = client.query(kind='comment')

    for entity in query.fetch():
        result.append(Comment(entity['user'], entity['text'], entity['time']))
    
    if rev:
        result.sort(reverse=rev)
    else:
        result.sort()
    
    return result


def ds_put_comment(ds_comment):
    client = get_client()
    client.put(ds_comment)


def clean(s):
    """Return a string w/ angle brackets, endlines, & tab characters removed."""

    s = s.replace('<', '&lt;')
    s = s.replace('>', '&gt;')
    s = s.replace('\n', ' ')
    s = s.replace('\t', ' ')
    s = s.strip()

    return s


class Comment():
    """An object representing a single chat comment."""

    def __init__(self, user, text, time=None):
        """Initialize a comment for named user."""

        self.user = user
        self.text = text

        if time:
            self.time = time
        else:
            self.time = datetime.datetime.now(datetime.timezone.utc)


    def get_formatted_time(self):
        """Return this comments' time as a 'YYYYMMDD HH:MM:SS' string."""

        return self.time.strftime('%Y%m%d %H:%M:%S')


    def __str__(self):
        """Return a simple formatted string with the comment contents."""

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

def add_comment(msg):
    """Add a comment to our comments list."""

    # Create comment entity in datastore and add comment fields to it
    ds_comment = ds_create_comment()
    ds_comment['user'] = msg.user
    ds_comment['text'] = msg.text
    ds_comment['time'] = msg.time

    try:
        ds_put_comment(ds_comment)
    except:
        return False


def create_comment(user, text):
    """Create a new comment with the current timestamp."""

    add_comment(Comment(clean(user), clean(text)))


def get_comments_list():
    """Return the current comment list as dict list"""

    result = []
    for comment in ds_get_comments():
        result.append({
            'user': comment.user,
            'text': comment.text,
            'time': comment.time
        })

    return result