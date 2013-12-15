import test_db
from middle.db import postgres

class Base(test_db.Base):
  @classmethod
  def connect(cls):
    return postgres.Connection(
      dbname = 'test',
      user = 'toddsifleet'
    )

class TestQuery(test_db.Query, Base):
  pass

class TestConstraints(test_db.Constraints, Base):
  pass

class TestQueryWithoutId(test_db.QueryWithoutId, Base):
  pass
