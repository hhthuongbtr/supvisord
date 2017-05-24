from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth import logout as auth_logout
from django.core.context_processors import csrf
from accounts.user_info import *
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect

def frontpage(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')
    else: 
        return render_to_response('frontpage.html')
            
# ------------auth
def login(request):
    c = {}
    c.update(csrf(request))        
    return render_to_response('accounts/login.html', c)
    
def auth_view(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = authenticate(username=username, password=password)
        
    if user is not None:
        if user.is_active:
            auth.login(request, user)
            return HttpResponseRedirect('/supvisor/')   
    else: 
        return HttpResponseRedirect('/accounts/invalid')
        
def invalid_login(request):
    return render_to_response('accounts/invalid_login.html')
    
"""def logout_view(request):
    auth_logout(request)
    response = render_to_response('accounts/login.html')
    response.delete_cookie('user_location')
    return response"""
def logout(request):
    auth_logout(request)
    return HttpResponseRedirect("/accounts/login/")


def test_login(request):
    agrs = user_info(request)
    print agrs
    print agrs['id']
    print agrs['email']
    return render_to_response('test_login.html',agrs)

def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('/accounts/login')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {
        'form': form
    })
