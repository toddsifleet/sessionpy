from test_db import Base
from middle.db import mysql
import tempfile
import os

class TestClass(Base):
  @classmethod
  def connect(cls):
    cls.file_handle = tempfile.NamedTemporaryFile(delete = False)
    return mysql.Connection(cls.file_handle.name)

  @classmethod
  def disconnect(cls):
    os.unlink(cls.file_handle.name)
