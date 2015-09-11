#coding=utf-8

from django.shortcuts import render_to_response
from django.http.response import HttpResponseRedirect, HttpResponse,\
    JsonResponse
from models import Users,Projects,Servers
from django.core.urlresolvers import reverse

import hashlib
import logging
import traceback
import paramiko
import json
from django.core import serializers
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
from LogsMgmt.models import Envs
import time

logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(filename)s [%(levelname)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
                filename='error.log',
                filemode='a')

# Create your views here.
def login(request):
    return render_to_response('login.html', {})

def set2md5(src):
    m = hashlib.md5()
    m.update(src)
    dest = m.hexdigest()
    return dest

pageSize=15
cryptKey='1wdvgy8uhbfe3rgy'
cryptMode = AES.MODE_CBC
def encrypt(text):
    cryptor = AES.new(cryptKey,cryptMode,b'0000000000000000')
    length = 16
    count = len(text)
    if count < length:
        add = (length-count)
        text = text + ('\0' * add)
    elif count > length:
        add = (length-(count % length))
        text = text + ('\0' * add)
    ciphertext = cryptor.encrypt(text)
    return b2a_hex(ciphertext)
     
def decrypt(text):
    cryptor = AES.new(cryptKey,cryptMode,b'0000000000000000')
    plain_text  = cryptor.decrypt(a2b_hex(text))
    return plain_text.rstrip('\0')
    
def loginChk(req):
    if req.method == 'POST':
        username = req.POST.get('username','')
        password = set2md5(req.POST.get('password',''))
        user = Users.objects.filter(username = username,password = password)
        if user:
            req.session['username'] = username
            return HttpResponseRedirect(reverse("welcome"))
        else:
            return HttpResponseRedirect(reverse("login"))

def home(req):
    return render_to_response('home.html' ,{'user':'Guest'})

def welcome(req):
    if req.session.get('username'):
        return render_to_response('welcome.html' ,{'user':req.session.get('username')})
    else:
        return HttpResponseRedirect(reverse("login"))

def passwd(req):
    if req.session.get('username'):
        return render_to_response('passwd.html' ,{'user':req.session.get('username')})
    else:
        return HttpResponseRedirect(reverse("login"))

def project(req):
    if req.session.get('username'):
        return render_to_response('project.html' ,{'user':req.session.get('username')})
    else:
        return HttpResponseRedirect(reverse("login"))


def server(req):
    if req.session.get('username'):
        return render_to_response('server.html' ,{'user':req.session.get('username')})
    else:
        return HttpResponseRedirect(reverse("login"))


def users(req):
    if req.session.get('username'):
        return render_to_response('users.html' ,{'user':req.session.get('username')})
    else:
        return HttpResponseRedirect(reverse("login"))

def logout(req):
    try:
        del req.session['username']
    except KeyError:
        pass
    return HttpResponseRedirect(reverse("login"))

def getLineNum(req):
    srvname=req.POST.get('srvName','')
    srv = Servers.objects.get(displayName=srvname)
    host = srv.ip
    port=int(srv.port)
    uname=srv.loginName
    passwd=decrypt(srv.loginPasswd)
    logDir=srv.logDir
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host,port,uname,passwd)
    transport = client.get_transport()
    transport.set_keepalive(1) 
    channel = transport.open_session()
    cmd="cat "+logDir+" |wc -l"
    channel.exec_command(cmd)
    try:
        lineNum=int(channel.recv(1024))
        if lineNum>10:
                lineNum = lineNum-10
        if lineNum == 0:
                lineNum = 1
        return HttpResponse(lineNum)
    except Exception:
        logging.error(traceback.format_exc())
    finally:   
        channel.close()
        client.close()

def getLineCount(req):
    srvname=req.POST.get('srvName','')
    srv = Servers.objects.get(displayName=srvname)
    host = srv.ip
    port=int(srv.port)
    uname=srv.loginName
    passwd=decrypt(srv.loginPasswd)
    logDir=srv.logDir
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host,port,uname,passwd)
    transport = client.get_transport()
    transport.set_keepalive(1) 
    channel = transport.open_session()
    cmd="cat "+logDir+" |wc -l"
    channel.exec_command(cmd)
    try:
        lineNum=int(channel.recv(1024))
        return HttpResponse(lineNum)
    except Exception:
        logging.error(traceback.format_exc())
    finally:   
        channel.close()
        client.close()

def getLastCount(host,port,uname,passwd,logDir):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host,port,uname,passwd)
        cmd="cat "+logDir+" |wc -l"
        stdin, stdout, stderr=client.exec_command(cmd)
        lastCount= stdout.read()
        return lastCount
    except Exception:
        logging.error(traceback.format_exc())
    finally:   
        client.close()
        
def printLog(req):
    if req.method == 'POST':
        srvname=req.POST.get('srvName','')
        lineNum=req.POST.get('lineNum','')
        try:
            srv = Servers.objects.get(displayName=srvname)
            host = srv.ip
            port=int(srv.port)
            uname=srv.loginName
            passwd=decrypt(srv.loginPasswd)
            logDir=srv.logDir
            ####
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(host,port,uname,passwd)
            time.sleep(1)
            newLineNo = int(getLastCount(host,port,uname,passwd,logDir))
            cmd="sed -n '"+lineNum+","+str(newLineNo)+"p' "+logDir
            stdin, stdout, stderr=client.exec_command(cmd)
            logContent= stdout.read()
            data = {'newLineNum': newLineNo,'logContent':logContent}
            return JsonResponse(data)
        except Exception:
            logging.error(traceback.format_exc())
        finally:   
            client.close()

def printHistoryLog(req):
    if req.method == 'POST':
        srvname=req.POST.get('srvName','')
        lineBeginNum=req.POST.get('lineBeginNum','')
        if lineBeginNum=='':
            lineBeginNum='1'
        lineEndNum=req.POST.get('lineEndNum','')
        if lineEndNum=='':
            lineEndNum='$'
        try:
            srv = Servers.objects.get(displayName=srvname)
            host = srv.ip
            port=int(srv.port)
            uname=srv.loginName
            passwd=decrypt(srv.loginPasswd)
            logDir=srv.logDir
            ####
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(host,port,uname,passwd)
            cmd="sed -n '"+lineBeginNum+","+lineEndNum+"p' "+logDir
            stdin, stdout, stderr=client.exec_command(cmd)
            logContent= stdout.readlines()
            return HttpResponse(logContent)
        except Exception:
            logging.error(traceback.format_exc())
        finally:   
            client.close()

def getAllUsers(req):
    try:
        data = serializers.serialize('json', Users.objects.all(), fields=('username', 'level','status'))
        return HttpResponse(data,content_type="application/json")
    except Exception:
        logging.error(traceback.format_exc())
        return HttpResponse("fail")

def updateUserStatus(req):
    if req.method == 'POST':
        name = req.POST.get('username','')
        status=req.POST.get('status','')
        try:
            Users.objects.filter(username=name).update(status=status)
            return HttpResponse("success")
        except Exception:
            logging.error(traceback.format_exc())
            return HttpResponse("fail")
        
def addUser(req):
    if req.method == 'POST':
        name = req.POST.get('username','')
        pswd = set2md5(req.POST.get('password',''))
        if Users.objects.filter(username=name):
            return HttpResponse("<script>alert('该用户已存在！');window.history.go(-1);</script>")
        else:
            try:
                Users.objects.create(username=name, password=pswd,level='1',status='0')
                return HttpResponseRedirect(reverse("users"))
            except Exception:
                logging.error(traceback.format_exc())

def delUser(req):
    if req.method == 'POST':
        name = req.POST.get('username','')
        try:
            p=Users.objects.get(username=name)
            p.delete()
            return HttpResponse("success")
        except Exception:
            logging.error(traceback.format_exc())
            return HttpResponse("fail")
        
def updatePassword(req):
    if req.session.get('username'):
        name=req.session.get('username')
        if req.method == 'POST':
            password = set2md5(req.POST.get('oldpwd',''))
            newpasswd = set2md5(req.POST.get('newpwd',''))
            try:
                user = Users.objects.filter(username = name,password = password)
                redPath = reverse("passwd").encode('utf-8')
                if user:
                    Users.objects.filter(username=name).update(password=newpasswd)                     
                    return HttpResponse("<script>alert('密码修改成功！');window.location.href='"+redPath+"'</script>")
                else:
                    return HttpResponse("<script>alert('原密码错误！');window.location.href='"+redPath+"'</script>")
            except Exception:
                logging.error(traceback.format_exc())
                return HttpResponse("fail")
    else:
        return HttpResponseRedirect(reverse("login"))
    
def getAllProjects(req):
    try:
        data = serializers.serialize('json', Projects.objects.all(), fields=('pjCode', 'pjName'))
        return HttpResponse(data,content_type="application/json")
    except Exception:
        logging.error(traceback.format_exc())
        return HttpResponse("fail")

def getProjectCount(req):
    if req.method == 'POST':
        try:
            pjCount = Projects.objects.count()
            data = {'pjCount': pjCount}
            return JsonResponse(data)
            #return HttpResponse(json.dumps(data),content_type="application/json")
        except Exception:
            logging.error(traceback.format_exc())
            return HttpResponse("fail")

def addProject(req):
    if req.method == 'POST':
        pjcode = req.POST.get('pjCode','')
        pjname =req.POST.get('pjName','')
        if Projects.objects.filter(pjCode=pjcode):
            return HttpResponse("<script>alert('该项目CODE已存在！');window.history.go(-1);</script>")
        else:
            try:
                Projects.objects.create(pjCode=pjcode, pjName=pjname)
                return HttpResponseRedirect(reverse("project"))
            except Exception:
                logging.error(traceback.format_exc())
                
def updateProject(req):
    if req.method == 'POST':
        pjcode = req.POST.get('pjCode','')
        pjname =req.POST.get('pjName','')
        redPath = reverse("project").encode('utf-8')
        try:
            Projects.objects.filter(pjCode=pjcode).update(pjName=pjname)
            return HttpResponse("<script>window.location.href='"+redPath+"'</script>")
        except Exception:
            logging.error(traceback.format_exc())
            return HttpResponse("fail")
        
def delProject(req):
    if req.method == 'POST':
        pjcode = req.POST.get('pjCode','')
        try:
            p=Projects.objects.get(pjCode=pjcode)
            p.delete()
            return HttpResponse("success")
        except Exception:
            logging.error(traceback.format_exc())
            return HttpResponse("fail")
        
def getAllServers(req):
    try:
        data = serializers.serialize('json', Servers.objects.select_related().all().order_by('id')[:pageSize], fields=('displayName', 'pj','env','ip','port','loginName','logDir'),use_natural_foreign_keys=True)
        return HttpResponse(data,content_type="application/json")
    except Exception:
        logging.error(traceback.format_exc())
        return HttpResponse("fail")

def getServerCount(req):
    if req.method == 'POST':
        try:
            srvCount = Servers.objects.count()
            data = {'srvCount': srvCount}
            return JsonResponse(data)
            #return HttpResponse(json.dumps(data),content_type="application/json")
        except Exception:
            logging.error(traceback.format_exc())
            return HttpResponse("fail")
        
def getAllEnvs(req):
    try:
        data = serializers.serialize('json', Envs.objects.all())
        return HttpResponse(data,content_type="application/json")
    except Exception:
        logging.error(traceback.format_exc())
        return HttpResponse("fail")

def addServer(req):
    if req.method == 'POST':
        srvName = req.POST.get('srvName','')
        srvIP = req.POST.get('srvIP','')
        srvPort = req.POST.get('srvPort','')
        loginUser = req.POST.get('loginUser','')
        loginPwd = encrypt(req.POST.get('loginPwd',''))
        logDir = req.POST.get('logDir','')
        pj = Projects.objects.get(pjName=req.POST.get('pjName',''))
        env = Envs.objects.get(envName=req.POST.get('env',''))
        if Servers.objects.filter(displayName=srvName):
            return HttpResponse("<script>alert('该服务器信息已存在！');window.history.go(-1);</script>")
        else:
            try:
                Servers.objects.create(displayName=srvName, ip=srvIP,port=srvPort,loginName=loginUser,loginPasswd=loginPwd, logDir=logDir,pj=pj,env=env)
                return HttpResponseRedirect(reverse("server"))
            except Exception:
                logging.error(traceback.format_exc())

def delServer(req):
    if req.method == 'POST':
        srvName = req.POST.get('srvName','')
        try:
            p=Servers.objects.get(displayName=srvName)
            p.delete()
            return HttpResponse("success")
        except Exception:
            logging.error(traceback.format_exc())
            return HttpResponse("fail")
        
def updateServer(req):
    if req.method == 'POST':
        srvName = req.POST.get('srvName','')
        srvIP = req.POST.get('srvIP','')
        srvPort = req.POST.get('srvPort','')
        loginUser = req.POST.get('loginUser','')
        loginPwd = encrypt(req.POST.get('loginPwd',''))
        logDir = req.POST.get('logDir','')
        pj = Projects.objects.get(pjName=req.POST.get('pjName',''))
        env = Envs.objects.get(envName=req.POST.get('env',''))
        redPath = reverse("server").encode('utf-8')
        try:
            Servers.objects.filter(displayName=srvName).update(ip=srvIP,port=srvPort,loginName=loginUser,loginPasswd=loginPwd,logDir=logDir,pj=pj,env=env)
            return HttpResponse("<script>window.location.href='"+redPath+"'</script>")
        except Exception:
            logging.error(traceback.format_exc())
            return HttpResponse("fail")

def getServerInfo(req):
    if req.method == 'POST':
        try:
            srvName = req.POST.get('srvName','')
            srv = Servers.objects.get(displayName=srvName)
            ip = srv.ip
            port=srv.port
            loginName=srv.loginName
            loginPasswd=decrypt(srv.loginPasswd)
            logDir=srv.logDir
            pj=srv.pj.pjName
            env=srv.env.envName
            data = {'ip': ip,'port':port,'loginName':loginName,'loginPasswd':loginPasswd,'logDir':logDir,'pjName':pj,'envName':env}
            return JsonResponse(data)
            #return HttpResponse(json.dumps(data),content_type="application/json")
        except Exception:
            logging.error(traceback.format_exc())
            return HttpResponse("fail")
    
def testConnServer(req):
    if req.method == 'POST':
        try:
            srvIP = req.POST.get('srvIP','')
            srvPort = int(req.POST.get('srvPort',''))
            loginUser = req.POST.get('loginUser','')
            loginPwd = req.POST.get('loginPwd','')
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(srvIP,srvPort,loginUser,loginPwd,timeout=5)
            return HttpResponse("connect success")
        except Exception:
            logging.error(traceback.format_exc())
            return HttpResponse("connect fail")
        finally:   
            client.close()
            
def getPageCount(req):
    if req.method == 'POST':
        try:
            srvCount = (Servers.objects.count()/pageSize)+1
            data = {'srvCount': srvCount}
            return JsonResponse(data)
            #return HttpResponse(json.dumps(data),content_type="application/json")
        except Exception:
            logging.error(traceback.format_exc())
            return HttpResponse("get page count fail")
        
def getPageServers(req):
    try:
        page=int(req.GET.get('page',''))
        startNum=(page-1)*pageSize
        endNum=page*pageSize
        data = serializers.serialize('json', Servers.objects.select_related().all().order_by('id')[startNum:endNum], fields=('displayName', 'pj','env','ip','port','loginName','logDir'),use_natural_foreign_keys=True)
        return HttpResponse(data,content_type="application/json")
    except Exception:
        logging.error(traceback.format_exc())
        return HttpResponse("fail")
    
def getFilterServers(req):
    try:
        keywd=req.GET.get('keyword','')
        qs1 = Servers.objects.select_related().filter(displayName__contains=keywd)
        qs2 = Servers.objects.select_related().filter(ip__contains=keywd)
        qs = qs1 | qs2
        qs = qs.distinct()
        data = serializers.serialize('json', qs.order_by('id'), fields=('displayName', 'pj','env','ip','port','loginName','logDir'),use_natural_foreign_keys=True)
        return HttpResponse(data,content_type="application/json")
    except Exception:
        logging.error(traceback.format_exc())
        return HttpResponse("fail")
    
def getLastServers(req):
    try:
        data = serializers.serialize('json', Servers.objects.select_related().all().reverse()[:2] , fields=('displayName', 'pj','env','ip','port','loginName','logDir'),use_natural_foreign_keys=True)
        return HttpResponse(data,content_type="application/json")
    except Exception:
        logging.error(traceback.format_exc())
        return HttpResponse("fail")
    
def getEnvForProject(req):
    try:
        pjname = req.GET.get('pjName','')
        pj = Projects.objects.get(pjName=pjname)
        srv=Servers.objects.select_related().values('env').filter(pj=pj).distinct()
        data_list=[] 
        for s in srv:
            data_list.append({"envName":Envs.objects.get(id=s['env']).envName})
        data = json.dumps(data_list)
        return HttpResponse(data,content_type="application/json")
    except Exception:
        logging.error(traceback.format_exc())
        return HttpResponse("fail")
    
def getProject2Env2Server(req):
    try:
        pjname = req.GET.get('pjName','')
        pj = Projects.objects.get(pjName=pjname)
        envname = req.GET.get('envName','')
        env = Envs.objects.get(envName=envname)
        data = serializers.serialize('json', Servers.objects.filter(env=env).filter(pj=pj), fields=('displayName'),use_natural_foreign_keys=True)
        return HttpResponse(data,content_type="application/json")
    except Exception:
        logging.error(traceback.format_exc())
        return HttpResponse("fail")