from django.db.models import Q
from log.models import *
from itertools import chain
from django.db import connection
from django.utils import timezone
from log.models import *
from accounts.user_info import *
from django.shortcuts import render_to_response

def write_log(user, action, msg):
	obj_log = Log(user=user, action = action, msg=msg)
	obj_log.save()

def log_view(request):
    log_list = Log.objects.all().order_by('-datetime')[:200]
    args = {}
    args['log_list'] = log_list
    args['id'] = request.user.id
    args['email'] = request.user.email if request.user.email else request.user.username
    args['is_superuser'] = 'true' if request.user.is_superuser else 'false'
    args['is_staff'] =  'true' if request.user.is_staff else 'false'
    return render_to_response('log/log.html', args)