import sys
from datetime import datetime, timedelta

sys.path.append('/Users/toddsifleet/Dropbox/github/sessionpy/sessionpy')

def now():
  return datetime.today().replace(microsecond=0)

def days_ago(n):
  return now() - timedelta(days = n)

