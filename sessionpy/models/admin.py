from models.base import Model
from models.user import User
from models.types import String, DateTime, Owner

import hashlib
import os


class AdminUser(User):
  def create_session(self, *args, **kwargs):
    return super(AdminUser, self).create_session(*args, **kwargs)

class AdminSession(Model):
  columns = (
    Owner(
      AdminUser,
      null = False
    ),
    DateTime('expires_at'),
    String('token',
      unique = True,
      indexed = True
    ),
  )
