from tests import base as test_utils
from authenticator import Authenticator
from middle.db import sqlite
from models.base import Model

import tempfile
import os

class DummyModel(Model):
  columns = ()

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

  def test_audit(self):
    DummyModel.init_table()
    time = test_utils.now()
    dummy = DummyModel.create()
    dummy = DummyModel.find_by_id(dummy.id)
    assert dummy.created_at == time
    assert dummy.updated_at == time
    DummyModel.drop_table()

