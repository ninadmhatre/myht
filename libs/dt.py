from flask_login import UserMixin


class User(UserMixin):
    """
    User object after login
    """

    def __init__(self, id_: str, email: str, access_token: str = None):
        self.id = id_
        self.email = email
        self.access_token = access_token

    def is_active(self):
        """True, as all users are active."""
        return True

    def is_anonymous(self):
        return self.id is None or self.email is None

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.email

    def get_email(self):
        """Get Email of the user"""
        return self.email

    def __repr__(self):
        return f"{self.__class__.__name__}(email={self.email}, id={self.id})"
