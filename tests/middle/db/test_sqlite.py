import test_db
from middle.db import sqlite
import tempfile
import os

class Base(test_db.Base):
  @classmethod
  def connect(cls):
    cls.file_handle = tempfile.NamedTemporaryFile(delete = False)
    return sqlite.Connection(db = cls.file_handle.name)

class TestQuery(test_db.Query, Base):
  @classmethod
  def disconnect(cls):
    os.unlink(cls.file_handle.name)


class TestConstraints(test_db.Constraints, Base):
  def test_length_of_string(self):
    # sqlite cannot support this
    pass

class TestQueryWithoutId(test_db.QueryWithoutId, Base):
  pass
