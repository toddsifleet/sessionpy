import test_db
from middle.db import mysql
import tempfile
import os

class Base(test_db.Base):
  @classmethod
  def connect(cls):
    return mysql.Connection('test')

class TestClass(test_db.Query, Base):
  pass

class TestConstraints(test_db.Constraints, Base):
  pass
