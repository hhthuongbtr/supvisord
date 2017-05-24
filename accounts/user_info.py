from django.http import HttpResponseRedirect, Http404, HttpResponse 
def user_info(request):
    args = {}
    args['id'] = request.user.id
    args['email'] = request.user.email if request.user.email else request.user.username
    args['is_superuser'] = 'true' if request.user.is_superuser else 'false'
    args['is_staff'] =  'true' if request.user.is_staff else 'false'
    return args


def check_auth(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/accounts/login')