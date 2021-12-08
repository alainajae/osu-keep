
from google.cloud import datastore

import objects
import logging


### Your data storage code goes here.
# Look at: https://console.cloud.google.com/datastore to see your live
# entities.


def _get_client():
    """Build a datastore client."""

    return datastore.Client('osu-keep')


def _load_key(client, entity_type, entity_id=None, parent_key=None):
    """Load a datastore key using a particular client, and if known, the ID.
    Note that the ID should be an int - we're allowing datastore to generate
    them in this example."""

    key = None
    if entity_id:
        key = client.key(entity_type, entity_id, parent=parent_key)
    else:
        # this will generate an ID
        key = client.key(entity_type)
    return key


def _load_entity(client, entity_type, entity_id, parent_key=None):
    """Load a datstore entity using a particular client, and the ID."""

    key = _load_key(client, entity_type, entity_id, parent_key)
    entity = client.get(key)
    logging.info('retrieved entity for %s' % (entity_id))
    return entity



def load_user(username, passwordhash):
    """Load a user based on the passwordhash; if the passwordhash doesn't match
    the username, then this should return None."""

    client = _get_client()
    q = client.query(kind=_USER_ENTITY)
    q.add_filter('username', '=', username)
    q.add_filter('passwordhash', '=', passwordhash)
    for user in q.fetch():
        return objects.User(user['username'], user['email'], user['about'])
    return None


def load_about_user(username):
    """Return a string that represents the "About Me" information a user has
    stored."""

    user = _load_entity(_get_client(), _USER_ENTITY, username)
    if user:
        return user['about']
    else:
        return ''



def save_user(user, passwordhash):
    """Save the user details to the datastore."""

    client = _get_client()
    entity = datastore.Entity(_load_key(client, _USER_ENTITY, user.username))
    entity['username'] = user.username
    entity['email'] = user.email
    entity['passwordhash'] = passwordhash
    entity['about'] = ''
    entity['completions'] = []
    client.put(entity)


def save_about_user(username, about):
    """Save the user's about info to the datastore."""

    client = _get_client()
    user = _load_entity(client, _USER_ENTITY, username)
    user['about'] = about
    client.put(user)


