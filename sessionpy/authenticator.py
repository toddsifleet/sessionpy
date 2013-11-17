from models.base import Model

class Authenticator(object):
  def __init__(self, db,  settings = None):
    Model.db = db

  def username_and_password(self, username, password):
    pass

  def email_and_password(self, email, password):
    pass

  def remember_me(self, remember_me_token):
    pass


