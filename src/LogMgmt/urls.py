#coding=utf-8
"""LogMgmt URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from LogsMgmt import views 
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.login),
    url(r'^login/$', views.login,name='login'),
    url(r'^logout/$', views.logout,name='logout'),
    url(r'^loginChk/$', views.loginChk,name='loginChk'),
    url(r'^home/$',views.home,name='home'),
    url(r'^welcome/$',views.welcome,name='welcome'),
    url(r'^passwd/$',views.passwd,name='passwd'),
    url(r'^server/$',views.server,name='server'),
    url(r'^users/$',views.users,name='users'),
    url(r'^project/$',views.project,name='project'),
    url(r'^getLineCount/$',views.getLineCount,name='getLineCount'),
    url(r'^getLineNum/$',views.getLineNum,name='getLineNum'),
    url(r'^printLog/$',views.printLog,name='printLog'),
    url(r'^printHistoryLog/$',views.printHistoryLog,name='printHistoryLog'),
    url(r'^getAllUsers/$',views.getAllUsers,name='getAllUsers'),
    url(r'^updateUserStatus/$',views.updateUserStatus,name='updateUserStatus'),
    url(r'^addUser/$',views.addUser,name='addUser'),
    url(r'^delUser/$',views.delUser,name='delUser'),
    url(r'^updatePassword/$',views.updatePassword,name='updatePassword'),
    url(r'^getAllProjects/$',views.getAllProjects,name='getAllProjects'),
    url(r'^addProject/$',views.addProject,name='addProject'),
    url(r'^updateProject/$',views.updateProject,name='updateProject'),
    url(r'^delProject/$',views.delProject,name='delProject'),
    url(r'^getAllServers/$',views.getAllServers,name='getAllServers'),
    url(r'^getAllEnvs/$',views.getAllEnvs,name='getAllEnvs'),
    url(r'^addServer/$',views.addServer,name='addServer'),
    url(r'^delServer/$',views.delServer,name='delServer'),
    url(r'^updateServer/$',views.updateServer,name='updateServer'),
    url(r'^getServerInfo/$',views.getServerInfo,name='getServerInfo'),
    url(r'^testConnServer/$',views.testConnServer,name='testConnServer'),
    url(r'^getPageCount/$',views.getPageCount,name='getPageCount'),
    url(r'^getPageServers/$',views.getPageServers,name='getPageServers'),
    url(r'^getFilterServers/$',views.getFilterServers,name='getFilterServers'),
    url(r'^getServerCount/$',views.getServerCount,name='getServerCount'),
    url(r'^getProjectCount/$',views.getProjectCount,name='getProjectCount'),
    url(r'^getLastServers/$',views.getLastServers,name='getLastServers'),
    url(r'^getEnvForProject/$',views.getEnvForProject,name='getEnvForProject'),
    url(r'^getProject2Env2Server/$',views.getProject2Env2Server,name='getProject2Env2Server'),
]+ static(settings.STATIC_URL)
