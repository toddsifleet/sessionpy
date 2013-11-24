import hashlib
import os

from models.base import Model

class User(Model):
  columns = (
    ('username', 'string', {'unique': True}),
    ('password', 'string'),
    ('salt', 'string'),
    ('email', 'string', {'unique': True})
  )

  @classmethod
  def create(cls, **kwargs):
    kwargs['salt'] = cls.generate_salt()
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
