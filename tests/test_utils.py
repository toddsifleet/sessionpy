import sys
import datetime

sys.path.append('/Users/toddsifleet/Dropbox/github/sessionpy/sessionpy')

def now():
  return datetime.datetime.today().replace(microsecond=0)

