import pytest
from test_model import Base
from models.session import Session
from models.user import User

class TestSession(Base):
  def test_without_user(self):
    with pytest.raises(Exception):
      Session.create(user = None)

  def test_with_user(self):
    user = User.create()
    result = Session.create(user = user)
    assert result.user == user

  def test_duplicate_tokens(self):
    user = User.create()
    Session.create(user = user, token = 'test_token')
    with pytest.raises(Exception):
      Session.create(user = user, token = 'test_token')
