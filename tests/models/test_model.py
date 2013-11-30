from tests import test_utils
from authenticator import Authenticator
from middle.db import sqlite
from models.base import Model
from middle.db.types import String

import tempfile
import os
import pytest

class DummyModel(Model):
  columns = (
    String('unique_col', unique = True),
    String('not_unique_col')
  )

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

  def teardown(self):
    pass


class TestDummyModel(Base):
  def setup(self):
    DummyModel.init_table()

  def teardown(self):
    DummyModel.drop_table()

  def test_audit(self):
    created_at = test_utils.days_ago(30)
    updated_at = test_utils.now()
    dummy = DummyModel.create(created_at = created_at)
    dummy = DummyModel.find_by_id(dummy.id)
    assert dummy.created_at == created_at
    assert dummy.updated_at == updated_at

  def test_get_by_unique(self):
    dummy = DummyModel.create(unique_col = 'test_string')
    DummyModel.create(unique_col = 'test_string_2')
    result = DummyModel.find_by_unique_col('test_string')
    assert result == dummy

  def test_get_by_non_unique(self):
    dummy = DummyModel.create(not_unique_col = 'test_string')
    DummyModel.create(not_unique_col = 'test_string_2')
    result = DummyModel.find_by_not_unique_col('test_string')
    assert result.next() == dummy

  def test_invalid_create_param(self):
    with pytest.raises(Exception):
      DummyModel.create(fake_name = 'test')
