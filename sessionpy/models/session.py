from models.base import Model
from models.types import String, Integer, DateTime

class Session(Model):
  columns = (
    DateTime('expires_at'),
    Integer('user_id', foreign_key = ('users', 'id')),
    String('token', unique = True),
  )
