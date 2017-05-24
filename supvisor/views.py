# coding: utf8
import json
from django.db.models import Q
from django.db import transaction, connection,IntegrityError
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, Http404, HttpResponse 
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.cache import cache

from supvisor.utils import *
from log.views import *
from accounts.user_info import *
import time
import os, sys, subprocess, shlex, re, fnmatch,signal
from subprocess import call

@csrf_exempt
def supvisor(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/accounts/login')
	user = user_info(request)
	return render_to_response('supvisor/supvisor.html',user)

def supvisor_json(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/accounts/login')
	configFileList = get_conf_files_list()
	args = []
	for job in configFileList:
		#job = job.strip( '.ini' )
		#print job
		args.append({'name'				: job if job else None,
					'state'				: Process(job).get_job_status() if job else None,
					'description'		: Process(job).job_status() if job else None,
					'command'			: File(job).get_command() if job else None,
					})
	json_data = json.dumps({"process": args})
	return HttpResponse(json_data, content_type='application/json', status=200)

@csrf_exempt
def start_job(request, name):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/accounts/login')
	user = user_info(request)
	args={}
	args['name'] = name
	typeStream=Streaming(name).get_type()
	args['typeStream'] = typeStream
	if typeStream == 'Facebook':
		args['ip'] = Facebook(name).get_ip()
		args['streamkey'] = Facebook(name).get_streamkey()
	if Streaming(name).get_type() == 'Youtube':
		args['ip'] = Youtube(name).get_ip()
		args['streamkey'] = Youtube(name).get_streamkey()
	if request.method == 'POST':
		#Restart job if user not input new infor
		if 'startWithOldInfo' in request.POST:
			Process(name).restart_job()
			return HttpResponseRedirect('/supvisor/')
		#End restart job if user not input new infor
		if 'saveAndStart' in request.POST:
			#Get new infor from template
			streamkey = request.POST.get('command', '').strip()
			ip = request.POST.get('ip', '').strip()
			event = request.POST.get('event', '').strip()
			#Return deffault ip if new ip is none
			if not ip:
				ip = '225.1.1.7:30120'
			#Get new infor from template
			#write log
			msg= str(timezone.now())+" user: "+request.user.username+" edit process "+name 
			write_log(request.user.username,"edit", msg)
			#Check new infor not change
			if Streaming(name).get_type() == 'Youtube':
				if Youtube(name).get_ip()==ip and Youtube(name).get_streamkey()==streamkey:
					Process(name).restart_job()
					return HttpResponseRedirect('/supvisor/')
			if Streaming(name).get_type() == 'Facebook':
				if Youtube(name).get_ip()==ip and Youtube(name).get_streamkey()==streamkey:
					Process(name).restart_job()
					return HttpResponseRedirect('/supvisor/')
			#End check new infor

			#Update job if new onfor and old infor different
			if event == "Facebook":
				Facebook(name).save(ip, streamkey)
				if Process(name).get_job_status() == 1:
					Process(name).stop_job()
				Process(name).update_job()
				Process(name).start_job()
				return HttpResponseRedirect('/supvisor/')
			if event == "Youtube":
				Youtube(name).save(ip, streamkey)
				if Process(name).get_job_status() == 1:
					Process(name).stop_job()
				Process(name).update_job()
				Process(name).start_job()
				return HttpResponseRedirect('/supvisor/')
			#End update job if new onfor and old infor different
	return render_to_response('supvisor/start.html', args)
	

def stop_job(request, name):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/accounts/login')
	if Process(name).get_job_status() != 0:
		msg= str(timezone.now())+" user: "+request.user.username+" stop process "+name 
		write_log(request.user.username,"stop", msg)
		Process(name).stop_job()
	return HttpResponseRedirect('/supvisor/')

@csrf_exempt
def add_process(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/accounts/login')
	if request.method == 'POST':
		if 'saveAndStart' in request.POST:
			#Get new infor from template
			streamkey = request.POST.get('command', '').strip()
			ip = request.POST.get('ip', '').strip()
			#Return deffault ip if new ip is none
			if not ip:
				ip = '225.1.1.7:30120'
			event = request.POST.get('event', '').strip()
			name = request.POST.get('name', '').strip()
			#Cut white space
			name = name.replace(" ", "")
			#End get new infor from template
			msg= str(timezone.now())+" user: "+request.user.username+" add process "+name 
			write_log(request.user.username,"add", msg)
			if event == "Facebook":
				Facebook(name).save(ip, streamkey)
				if Process(name).get_job_status() == 1:
					Process(name).stop_job()
				Process(name).update_job()
				Process(name).start_job()
				return HttpResponseRedirect('/supvisor/')
			if event == "Youtube":
				Youtube(name).save(ip, streamkey)
				if Process(name).get_job_status() == 1:
					Process(name).stop_job()
				Process(name).update_job()
				Process(name).start_job()
				return HttpResponseRedirect('/supvisor/')
	return render_to_response('supvisor/add.html')

def delete_process(request, name):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/accounts/login')
	if Process(name).job_status:
		pass
	if Process(name).get_job_status() == 1:
		return HttpResponse("<alert>Process is RUNNING, you need stop process!</alert>")
	else:
		msg= str(timezone.now())+" user: "+request.user.username+" delete process "+name 
		write_log(request.user.username,"delete", msg)
		Process(name).stop_job()
		File(name).delete()
		Process(name).update_job()
	return HttpResponseRedirect('/supvisor/')

def document(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/accounts/login')
	user = user_info(request)
	return render_to_response('supvisor/document.html', user)

#RTMP
@csrf_exempt
def rtmp_add_process(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/accounts/login')
	if request.method == 'POST':
		if 'saveAndStart' in request.POST:
			#Get new infor from template
			domain = request.POST.get('domain', '').strip()
			ip = request.POST.get('ip', '').strip()
			#Return deffault ip if new ip is none
			if not ip:
				ip = '225.1.1.7:30120'
			name = request.POST.get('name', '').strip()
			#Cut white space
			name = name.replace(" ", "")
			#End get new infor from template
			RTMP(name).save(ip, domain)
			if Process(name).get_job_status() == 1:
				Process(name).stop_job()
			Process(name).update_job()
			Process(name).start_job()
			return HttpResponseRedirect('/supvisor/')
	return render_to_response('supvisor/rtmp/add.html')