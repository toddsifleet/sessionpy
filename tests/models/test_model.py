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
    cls.connect()

  @classmethod
  def connect(cls):
    db = pytest.config.getoption('--db')
    base_path = '/Users/toddsifleet/Dropbox/github/sessionpy/tests/models/'
    if db == 'sqlite':
      cls.authenticator = Authenticator(base_path + 'sqlite.config',
        db = {
          'db': cls.file_handle.name
        }
      )
    else:
      cls.authenticator = Authenticator(base_path + db + '.config')

  @classmethod
  def teardown_class(cls):
    Model.db.commit()
    os.unlink(cls.file_handle.name)

  @classmethod
  def setup(self):
    Model.db.start_transaction()
    self.authenticator.drop_tables()
    self.authenticator.init_tables()

  def teardown(self):
    Model.db.rollback()


class TestDummyModel(Base):
  def setup(self):
    model_types = [DummyModel, DummyOwner]
    map(lambda x: x.drop_table(), model_types)
    map(lambda x: x.init_table(), model_types[::-1])

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
    assert result.first == dummy

  def test_invalid_create_param(self):
    with pytest.raises(Exception):
      DummyModel.create(fake_name = 'test')

  def test_owner(self):
    owner = DummyOwner.create()
    owned = DummyModel.create(**{
      DummyOwner.name: owner
    })

    owned = DummyModel.find_by_id(owned.id)
    assert owned.fetch_dummy_owner() == owner

    owner = DummyOwner.find_by_id(owner.id)
    assert owned in owner.dummy_models().all

