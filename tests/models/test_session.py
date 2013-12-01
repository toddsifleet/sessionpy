import pytest
from test_model import Base
from models.session import Session
from models.user import User

class TestSession(Base):
  def test_without_user(self):
    with pytest.raises(Exception):
      Session.create(user_id = 123421231)

  def test_with_user(self):
    user = User.create()
    result = Session.create(user_id = user.id)
    assert result.user_id == user.id

  def test_duplicate_tokens(self):
    user = User.create()
    Session.create(user_id = user.id, token = 'test_token')
    with pytest.raises(Exception):
      Session.create(user_id = user.id, token = 'test_token')
