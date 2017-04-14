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
import os.path
from subprocess import call

"""
import os.path, time
print("last modified: %s" % time.ctime(os.path.getmtime(file)))
print("created: %s" %       time.ctime(os.path.getctime(file)))
"""
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
		if request.user.is_superuser:
			args.append({'name'				: job if job else None,
						'state'				: 10+Process(job).get_job_status() if job.startswith("rtmp") else Process(job).get_job_status(),
						'description'		: Process(job).job_status() if job else None,
						'command'			: File(job).get_command() if job else None,
						#'dcreate'			: File(job).get_created() if job else '',
						'dmodified'			: File(job).get_last_modified() if job else '',
						})
		elif job.startswith(request.user.username):
			args.append({'name'				: job if job else None,
						'state'				: Process(job).get_job_status() if job else None,
						'description'		: Process(job).job_status() if job else None,
						'command'			: File(job).get_command() if job else None,
						#'dcreate'			: File(job).get_created() if job else '',
						'dmodify'			: File(job).get_last_modified() if job else '',
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
	elif Streaming(name).get_type() == 'Youtube':
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
			msg= " user: "+request.user.username+" edit process "+name 
			write_log(request.user.username,"edit", msg)
			#End check new infor

			#Update job if new onfor and old infor different
			if event == "Facebook":
				Facebook(name).save(ip, streamkey)
			elif event == "Youtube":
				Youtube(name).save(ip, streamkey)
			if Process(name).get_job_status() == 1:
				Process(name).stop_job()
			Process(name).update_job()
			Process(name).start_job()
			return HttpResponseRedirect('/supvisor/')
	return render_to_response('supvisor/start.html', args)	

def stop_job(request, name):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/accounts/login')
	if Process(name).get_job_status() != 0:
		msg= " user: "+request.user.username+" stop process "+name 
		write_log(request.user.username,"stop", msg)
		Process(name).stop_job()
	return HttpResponseRedirect('/supvisor/')

@csrf_exempt
def add_process(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/accounts/login')
	if request.method == 'POST':
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
		#add user name to file name
		name = request.user.username + '_'+name
		#End get new infor from template
		msg= " user: "+request.user.username+" add process "+name 
		write_log(request.user.username,"add", msg)
		if 'saveAndStart' in request.POST:
			msg= " user: "+request.user.username+" start process "+name 
			write_log(request.user.username,"start", msg)
			if event == "Facebook":
				Facebook(name).save(ip, streamkey)
				if Process(name).get_job_status() == 1:
					Process(name).stop_job()
				Process(name).update_job()
				Process(name).start_job()
			elif event == "Youtube":
				Youtube(name).save(ip, streamkey)
				if Process(name).get_job_status() == 1:
					Process(name).stop_job()
				Process(name).update_job()
				Process(name).start_job()
		elif 'saveOnly' in request.POST:
			if event == "Facebook":
				Facebook(name).save(ip, streamkey)
			elif event == "Youtube":
				Youtube(name).save(ip, streamkey)
			Process(name).update_job()
			Process(name).stop_job()
	return HttpResponseRedirect('/supvisor/')

def delete_process(request, name):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/accounts/login')
	if Process(name).job_status:
		pass
	if Process(name).get_job_status() == 1:
		return HttpResponse("<alert>Process is RUNNING, you need stop process!</alert>")
	else:
		msg= " user: "+request.user.username+" delete process "+name 
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
	if not request.user.is_superuser:
		return HttpResponseRedirect('/supvisor/')
	if request.method == 'POST':
		#Get new infor from template
		domain = request.POST.get('domain', '').strip()
		if domain.startswith("rtmp://"):
			domain = domain.replace("rtmp://","")
		ip = request.POST.get('ip', '').strip()
		name = request.POST.get('name', '').strip()
		#Cut white space
		name = name.replace(" ", "")
		#add user name to file name
		name = 'rtmp_'+name
		encode = request.POST.get('encode', '').strip()
		#End get new infor from template
		msg= " user: "+request.user.username+" add process "+name 
		write_log(request.user.username,"add", msg)
		if 'saveAndStart' in request.POST:
			rtmp_pattern=re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\:30120")
			aa = re.findall(rtmp_pattern, ip)
			if aa:
				RTMP(name).save_udp(ip, encode, domain)
			else:
				RTMP(name).save_rtmp(ip, encode, domain)

			if Process(name).get_job_status() == 1:
				Process(name).stop_job()
			Process(name).update_job()
			Process(name).start_job()
			msg= " user: "+request.user.username+" start process "+name 
			write_log(request.user.username,"start", msg)

		elif 'saveOnly' in request.POST:
			'''Save command'''
			rtmp_pattern=re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\:30120")
			aa = re.findall(rtmp_pattern, ip)
			if aa:
				RTMP(name).save_udp(ip, encode, domain)
			else:
				RTMP(name).save_rtmp(ip, encode, domain)
			'''End save command'''
			Process(name).update_job()
			Process(name).stop_job()
		return HttpResponseRedirect('/supvisor/')
	return render_to_response('supvisor/rtmp/add.html')

def rtmp_add_json(request):
	#if not request.user.is_authenticated():
	#	return HttpResponseRedirect('/accounts/login')
	configString =  File("rtmp.json.template").read_template()
	data = json.loads(configString)
	args = []
	args.append({'binary_system'		: data["binary_system"] if data["binary_system"] else "",
				'encode'				: data["encode"] if data["encode"] else "",
				'ip'					: data["ip"] if data["ip"] else "",
				'domain'				: data["domain"] if data["domain"] else "",
					})
	json_data = json.dumps({"rtmp": args})
	return HttpResponse(json_data, content_type='application/json', status=200)

@csrf_exempt
def rtmp_start_job(request, name):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/accounts/login')
	else:
		Process(name).update_job()
		Process(name).start_job()
		msg= " user: "+request.user.username+" start process "+name 
		write_log(request.user.username,"start", msg)
	return HttpResponseRedirect('/supvisor/')

@csrf_exempt
def rtmp_restart_job(request, name):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/accounts/login')
	else:
		if Process(name).get_job_status() == 1:
			Process(name).stop_job()
		Process(name).update_job()
		Process(name).start_job()
		msg= " user: "+request.user.username+" restart process "+name 
		write_log(request.user.username,"restart", msg)
	return HttpResponseRedirect('/supvisor/')

@csrf_exempt
def rtmp_edit_job(request, name):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/accounts/login')
	if request.method == 'POST':
		if 'saveAndStart' in request.POST:
			#Get new infor from template
			encode = request.POST.get('encode', '').strip()
			print encode
			domain = request.POST.get('domain', '').strip()
			print domain
			ip = request.POST.get('ip', '').strip()	
			print ip
			#check infor is change
			if RTMP(name).get_source()==ip and RTMP(name).get_encode()==encode and RTMP(name).get_destination()==domain:
				Process(name).restart_job()
				return HttpResponseRedirect('/supvisor/')
			'''Save command'''
			rtmp_pattern=re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\:30120")
			aa = re.findall(rtmp_pattern, ip)
			if aa:
				RTMP(name).save_udp(ip, encode, domain)
			else:
				RTMP(name).save_rtmp(ip, encode, domain)
			'''End save command'''

			if Process(name).get_job_status() == 1:
				Process(name).stop_job()
			Process(name).update_job()
			Process(name).start_job()
			msg= " user: "+request.user.username+" edit process "+name 
			write_log(request.user.username,"edit", msg)
		return HttpResponseRedirect('/supvisor/')
	else:
		user = user_info(request)
		args={}
		args['name'] = name
		args['ip'] = RTMP(name).get_source()
		args['domain'] = RTMP(name).get_destination()
		args['encode'] = RTMP(name).get_encode()
		return render_to_response('supvisor/rtmp/edit.html', args)