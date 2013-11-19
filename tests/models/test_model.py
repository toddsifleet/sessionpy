from tests import base
from authenticator import Authenticator
from middle.db import sqlite
import tempfile
import os

class Base(object):
  @classmethod
  def setup_class(cls):
    cls.file_handle = tempfile.NamedTemporaryFile(delete = False)
    conn = sqlite.Connection(cls.file_handle.name)
    Authenticator(conn)

  @classmethod
  def teardown_class(cls):
    os.unlink(cls.file_handle.name)

  def setup(self):
    pass

  def teardown(cls):
    pass

