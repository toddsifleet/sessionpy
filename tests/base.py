import sys
import datetime

sys.path.append('../sessionpy')

def now():
  return datetime.datetime.today().replace(microsecond=0)

