from django.db.models import Q
from log.models import *
from itertools import chain
from django.db import connection
from django.utils import timezone
from log.models import *

def write_log(user, action, msg):
	date_time = str(timezone.now())
	obj_log = Log(datetime=date_time, user=user, action = action, msg=msg)
	obj_log.save()
	print "write"
