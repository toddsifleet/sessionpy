from tests import test_utils
from authenticator import Authenticator
from middle.db import sqlite, mysql, postgres
from models.base import Model
from models.types import String, Owner
from models.user import User
from models.session import Session

import tempfile
import os
import pytest

class DummyOwner(Model):
  columns = tuple()

class DummyModel(Model):
  columns = (
    String('unique_col', unique = True),
    String('not_unique_col'),
    Owner(DummyOwner)
  )

class Base(object):
  @classmethod
  def setup_class(cls):
    cls.file_handle = tempfile.NamedTemporaryFile(delete = False)
    conn = cls.connect()
    Authenticator(conn)

  @classmethod
  def connect(cls):
    db = pytest.config.getoption('--db')
    if db == 'sqlite':
      return sqlite.Connection(cls.file_handle.name)
    elif db == 'mysql':
      return mysql.Connection('test')
    elif db == 'postgres':
      return postgres.Connection('test')

  @classmethod
  def teardown_class(cls):
    os.unlink(cls.file_handle.name)

  def setup(self):
    Session.drop_table()
    User.drop_table()
    User.init_table()
    Session.init_table()

  def teardown(self):
    pass


class TestDummyModel(Base):
  def setup(self):
    model_types = [DummyModel, DummyOwner]
    map(lambda x: x.drop_table(), model_types)
    map(lambda x: x.init_table(), model_types[::-1])

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

  def test_owner(self):
    owner = DummyOwner.create()
    parent = DummyModel.create(**{
      DummyOwner.name: owner
    })

    parent = DummyModel.find_by_id(parent.id)
    assert parent.fetch_dummy_owner() == owner

