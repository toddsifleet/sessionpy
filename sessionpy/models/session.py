from models.base import Model
from models.user import User
from models.types import String, Integer, DateTime, Owner

class Session(Model):
  columns = (
    Owner(User, null = False),
    DateTime('expires_at'),
    String('token', unique = True),
  )
