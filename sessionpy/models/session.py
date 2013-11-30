from models.base import Model
from middle.db.types import String, Integer, DateTime

class Session(Model):
  columns = (
    DateTime('expires_at'),
    Integer('user_id', foreign_key = ('users', 'id'))
  )
