from test_db import Base
from middle.db import postgres

class TestClass(Base):
  @classmethod
  def connect(cls):
    return postgres.Connection('test')

