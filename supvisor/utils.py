import json
import os, sys, subprocess, shlex, re, fnmatch,signal
from subprocess import call
import time
import re
import datetime
from datetime import datetime



fileDir = '/etc/supervisord.d/supervisor.conf/'
templateDir = '/etc/supervisord.d/template/'
configFileList = os.listdir(fileDir)
extention = '.ini'
bathService= '/etc/init.d/supervisord'
bathControl= '/usr/bin/supervisorctl'

def get_conf_files_list():
        return os.listdir(fileDir)
###########################################################################################
#                                                                                         #
#------------------------------------------FILE-------------------------------------------#
#                                                                                         #
###########################################################################################

class File:
    def __init__(self, fileName):
        if fileName.find(extention) >= 0 or fileName.find('template') >=0:
            self.fileName = fileName
        else:
            self.fileName = fileName+extention
        self.confFile= fileDir
        self.template= templateDir

    def read_template(self):
        f = open(self.template + self.fileName, 'r')
        lines=f.read()
        f.close()
        return lines

    def get_command_template(self):
        f = open(self.template + self.fileName, 'r')
        lines=f.readlines()
        f.close()
        return lines[1]

    def read_file(self):
        f = open(self.confFile + self.fileName, 'r')
        lines=f.read()
        f.close()
        return lines

    def get_command(self):
        f = open(self.confFile + self.fileName, 'r')
        lines=f.readlines()
        f.close()
        if (len(lines)) > 1:
            return lines[1]
        return 'Invalid configuration file!'

    def get_program_name(self):
        f = open(self.confFile + self.fileName, 'r')
        lines=f.readlines()
        f.close()
        if (len(lines)) > 0:
            return lines[0]
        return ''

    def write_conf_file(self, text):
        f = open(self.confFile + self.fileName, 'w')
        f.write(text)
        f.close()

    def delete(self):
        cmnd = ['/bin/rm', '-rf', self.confFile+self.fileName]
        p = subprocess.call(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(1)

    def get_created(self):
        return time.ctime(os.path.getctime(self.confFile+self.fileName))

    def get_last_modified(self):
        return time.ctime(os.path.getmtime(self.confFile+self.fileName))

###########################################################################################
#                                                                                         #
#----------------------------------------REGEX---------------------------------------------#
#                                                                                         #
###########################################################################################
class Regex:
    def __init__(self, str):
        self.str = str
    def get_ip_multicast(self):
        udp_pattern=re.compile("udp://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\:\d{2,5}")
        aa = re.findall(udp_pattern, self.str)
        if aa:
            return aa[0]
        else:
            return None

    def get_link(self):
        rtmp_pattern=re.compile("rtmp://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
        aa = re.findall(rtmp_pattern, self.str)
        if aa:
            if len(aa) == 2:
                return (aa[0], aa[1])
            else:
                return aa[0]
        else:
            return None


###########################################################################################
#                                                                                         #
#----------------------------------------STREAMING----------------------------------------#
#                                                                                         #
###########################################################################################
class Streaming:
    def __init__(self, fileName):
        if fileName.find(extention) > 0:
            self.fileName = fileName
        else:
            self.fileName = fileName+extention
    def get_type(self):
        command=File(self.fileName).get_command()
        if command.find('facebook') >=0:
            return "Facebook"
        elif command.find('youtube') >=0:
            return "Youtube"
        elif self.fileName.startswith("rtmp"):
            return "rtmp"
        return "Unknow"



###########################################################################################
#                                                                                         #
#----------------------------------------FACEBOOK-----------------------------------------#
#                                                                                         #
###########################################################################################
class Facebook:
    def __init__(self, fileName):
        if fileName.find(extention) > 0:
            self.fileName = fileName
        else:
            self.fileName = fileName+extention
        self.keySearchIP = 'udp://'
        self.endKeySearchIP = ' '
        self.keySearchStreamKey = '/rtmp/'
        self.endKeySearchStreamKey = '\n'

    def get_ip(self):
        command=File(self.fileName).get_command()
        return command[command.find(self.keySearchIP) + len(self.keySearchIP): command.find(self.endKeySearchIP, command.find(self.keySearchIP))]

    def get_streamkey(self):
        command=File(self.fileName).get_command()
        return command[command.find(self.keySearchStreamKey) + len(self.keySearchStreamKey) : command.find(self.endKeySearchStreamKey)]

    def save(self, ip, streamKey):
        text=File('facebook.template').read_template()
        #edit name
        text=text.replace('name', self.fileName)
        #edit ip
        text=text.replace('ip',ip)
        #edit stream key
        text=text.replace('streamkey', streamKey)
        File(self.fileName).write_conf_file(text)
###########################################################################################
#                                                                                         #
#----------------------------------------YOUTUBE------------------------------------------#
#                                                                                         #
###########################################################################################
class Youtube:
    def __init__(self, fileName):
        if fileName.find(extention) > 0:
            self.fileName = fileName
        else:
            self.fileName = fileName+extention
        self.keySearchIP = 'udp://'
        self.endKeySearchIP = ' '
        self.keySearchStreamKey = '/live2/'
        self.endKeySearchStreamKey = '\n'

    def get_ip(self):
        command=File(self.fileName).get_command()
        return command[command.find(self.keySearchIP) + len(self.keySearchIP): command.find(self.endKeySearchIP, command.find(self.keySearchIP))]

    def get_streamkey(self):
        command=File(self.fileName).get_command()
        return command[command.find(self.keySearchStreamKey) + len(self.keySearchStreamKey) : command.find(self.endKeySearchStreamKey)]

    def save(self, ip, streamKey):
        text=File('youtube.template').read_template()
        #eidt Name
        text=text.replace('name',self.fileName)
        #edit ip
        text=text.replace('ip',ip)
        #edit stream key
        text=text.replace('streamkey', streamKey)
        File(self.fileName).write_conf_file(text)

###########################################################################################
#                                                                                         #
#------------------------------------------SEVER------------------------------------------#
#                                                                                         #
###########################################################################################

class Server:
    def __init__(self):
        self.bath = bathService

    #0 is stop
    #1 is running
    def get_service_status(self):
        cmnd = [self.bath, 'status']
        p = subprocess.Popen(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        status = str(p.communicate())
        if status.find('unix') > 0:
            return 0
        return 1
    def start_service(self):
        cmnd = [self.bath, 'start']
        p = subprocess.call(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(5)

    def stop_service(self):
        cmnd = [self.bath, 'stop']
        p = subprocess.call(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(5)

    def restart_service(self):
        cmnd = [self.bath, 'restart']
        p = subprocess.call(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(5)
###########################################################################################
#                                                                                         #
#----------------------------------------PROCESS------------------------------------------#
#                                                                                         #
###########################################################################################

class Process:
    def __init__(self, jobName):
        if jobName.find(extention) > 0:
            self.jobName = jobName
        else:
            self.jobName = jobName+extention
        self.bath = bathControl

    def job_status(self):
        cmnd=[self.bath, 'status', self.jobName]
        p = subprocess.Popen(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        status = str(p.communicate())
        #print status
        #print str(status)
        status = status[status.rfind("     ") +5 : status.rfind(',')-3]
        return status
    #0 is stop
    #1 is running
    #2 is unknow eror
    #3 is server eror
    def get_job_status(self):
        if not Server().get_service_status():
            return 3
        status = self.job_status()
        if status.find('RUNNING') >= 0:
            return 1
        if status.find('STOPPED') >= 0:
            return 0
        return 2

    def update_job(self):
        cmnd = [self.bath, 'update']
        p = subprocess.call(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(1)

    def start_job(self):
        cmnd = [self.bath, 'start', self.jobName]
        p = subprocess.call(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(1)

    def stop_job(self):
        cmnd = [self.bath, 'stop', self.jobName]
        p = subprocess.call(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(1)

    def restart_job(self):
        cmnd = [self.bath, 'restart', self.jobName]
        p = subprocess.call(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(1)


    def job_status(self):
        cmnd=[self.bath, 'status', self.jobName]
        p = subprocess.Popen(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        status = str(p.communicate())
        #print status
        #print str(status)
        status = status[status.rfind("     ") +3 : status.rfind(',')-3]
        return status
#End class


###########################################################################################
#                                                                                         #
#----------------------------------------RTMP---------------------------------------------#
#                                                                                         #
###########################################################################################
class RTMP:
    def __init__(self, fileName):
        if fileName.find(extention) > 0:
            self.fileName = fileName
        else:
            self.fileName = fileName+extention
        self.keySearchIP = 'udp://'
        self.endKeySearchIP = ' '
        self.fristkeySearchEncode = 'udp://'
        self.secondKeySearchEncode = ' '
        self.endKeySearchEncode = 'rtmp://'
        self.keySearchDomain = 'rtmp://'
        self.endKeySearchDomain = '\n'

    def get_source(self):
        command=File(self.fileName).get_command()
        ip = Regex(command).get_ip_multicast()
        if ip:
            return ip.replace('udp://','')
        else:
            source, destination = Regex(command).get_link()
            return source.replace('rtmp://','')


    def get_destination(self):
        command=File(self.fileName).get_command()
        if len(Regex(command).get_link()) == 2:
            source, destination = Regex(command).get_link()
            return destination.replace('rtmp://','')
        else:
            destination = Regex(command).get_link()
            return destination.replace('rtmp://','')

    def get_encode(self):
        command=File(self.fileName).get_command()
        source = self.get_source()
        destination = self.get_destination()
        return command[command.find(source)+len(source) + 1 : command.find(destination) - len('rtmp:// ')]

    def save_udp(self, ip, encode, domain):
        #read template supervisord config
        text=File('rtmp.udp.template').read_template()
        #read config rtmp template as json data
        configString =  File("rtmp.json.template").read_template()
        #Convert to json data
        data = json.loads(configString)
        #edit encode
        text=text.replace('[encode]', encode)
        #edit name
        text=text.replace('[name]', self.fileName)
        #edit binary system name
        text=text.replace('[binary_system]', data["binary_system"])
        #edit ip
        text=text.replace('[ip]', ip)
        #edit stream key
        text=text.replace('[domain]', domain)
        File(self.fileName).write_conf_file(text)

    def save_rtmp(self, ip, encode, domain):
        #read template supervisord config
        text=File('rtmp.rtmp.template').read_template()
        #read config rtmp template as json data
        configString =  File("rtmp.json.template").read_template()
        #Convert to json data
        data = json.loads(configString)
        #edit encode
        text=text.replace('[encode]', encode)
        #edit name
        text=text.replace('[name]', self.fileName)
        #edit binary system name
        text=text.replace('[binary_system]', data["binary_system"])
        #edit ip
        text=text.replace('[ip]', ip)
        #edit stream key
        text=text.replace('[domain]', domain)
        File(self.fileName).write_conf_file(text)

class DateTime:
    def conver_human_creadeble_2_unix_timetamp(self, date_time):
        return int(time.mktime(time.strptime(date_time, '%Y-%m-%d %H:%M:%S')))

    def conver_human_creadeble_2_unix_timetamp_local(self, date_time):
        date_time_pattern = re.compile("\d{4}[/.-]\d{2}[/.-]\d{2} \d{2}:\d{2}:\d{2}")
        date_time_data = re.findall(date_time_pattern, date_time)
        date_time = date_time_data[0]
        return int(time.mktime(time.strptime(date_time, '%Y-%m-%d %H:%M:%S'))) - time.timezone

    def get_now(self):
        now = time.time()
        now_pattern = re.compile("\d+") 
        now = re.findall(now_pattern, str(now))
        now = now[0]
        return now

    def convert_date_pattern_2_unix_timestamp(self, ss, mm, hh, DD, MM, YYYY):
        human_date = "%s-%s-%s %s:%s:%s"%(YYYY,MM,DD,hh,mm,ss)
        return (int(time.mktime(time.strptime(human_date, '%Y-%m-%d %H:%M:%S')))) #- time.timezone)
        
    #data input string YYYY-MM-DDTHH:mm:ss.000Z, return a string
    def conver_UTC_2_unix_timestamp(self, utc_time):
        ts = time.strptime(utc_time[:19], "%Y-%m-%dT%H:%M:%S")
        human_date = time.strftime("%Y-%m-%d %H:%M:%S", ts)
        return (int(time.mktime(time.strptime(human_date, '%Y-%m-%d %H:%M:%S'))) - time.timezone)

    def get_now_as_human_creadeble(self):
        return (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    def convert_unix_timestamp_2_human_creadeble(self, timestamp):
        return (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(timestamp))))

    def get_now_as_isofortmat(self):
        now = datetime.datetime.now()
        format_iso_now = now.isoformat()
        return format_iso_now

    def get_hour(self, unix_timestamp):
        dt = datetime.fromtimestamp(unix_timestamp)
        return dt.hour

