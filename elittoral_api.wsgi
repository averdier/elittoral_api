import sys

if sys.version_info[0] < 3:
    raise Exception("Python3 required! Current (wrong) version: '%s'" % sys.version_info)

sys.path.insert(0, 'var/www/dev/elittoral_api')
from runserver import app as application