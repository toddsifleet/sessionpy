from test_db import Base
from middle.db import mysql
import tempfile
import os

class TestClass(Base):
  @classmethod
  def connect(cls):
    return mysql.Connection('test')

