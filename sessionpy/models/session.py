from models.base import Model
from models.user import User
from models.types import String, DateTime, Owner
import os

class Session(Model):
  columns = (
    Owner(User, null = False),
    DateTime('expires_at'),
    String('token',
      unique = True,
      indexed = True,
      length = 25
    ),
  )

  @classmethod
  def create(cls, *args, **kwargs):
    if 'token' not in kwargs:
      kwargs['token'] = os.urandom(8).encode('base_64')

    return super(Session, cls).create(**kwargs)
