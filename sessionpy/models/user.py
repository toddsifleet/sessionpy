import hashlib
import os

from models.base import Model
from models.types import String

class User(Model):
  columns = (
    String('username',
      unique = True,
      indexed = True
    ),
    String('email', unique = True),
    String('password', length = 512),
    String('salt', length = 512),
  )

  @classmethod
  def create(cls, **kwargs):
    kwargs['salt'] = cls.generate_salt()
    if 'password' in kwargs:
      kwargs['password'] = cls.hash_password(
        kwargs['password'],
        kwargs['salt']
      )
    return super(User, cls).create(**kwargs)

  @classmethod
  def generate_salt(cls):
    return os.urandom(96).encode('base_64')

  @classmethod
  def hash_password(cls, pw, salt):
    return hashlib.sha512(pw + salt).hexdigest()

  @classmethod
  def login(cls, username_or_email, password):
    user = cls.find_by_username(username_or_email) or\
      cls.find_by_email(username_or_email)

    if user and user.verify_password(password):
      user.create_session(user.id)
      return user

  @classmethod
  def extend_session(cls, token):
    pass

  def create_session(self, user_id):
    pass

  def verify_password(self, password):
    pw_hash = self.hash_password(password, self.salt)
    return pw_hash == self.password
