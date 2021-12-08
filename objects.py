
class User(object):
    """A user for the application."""

    def __init__(self, username, email, about=''):
        self.username = username
        self.email = email
        self.about = about

    def to_dict(self):
        return {
            'username': self.username,
            'about': self.about,
            'email': self.email,
        }