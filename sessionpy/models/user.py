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
    user = super(User, cls).create(**kwargs)
    return user

  @classmethod
  def generate_salt(cls):
    return os.urandom(96).encode('base_64')

  @classmethod
  def hash_password(cls, pw, salt):
    return hashlib.sha512(pw + salt).hexdigest()

  def verify_password(self, password):
    pw_hash = self.hash_password(password, self.salt)
    return pw_hash == self.password
