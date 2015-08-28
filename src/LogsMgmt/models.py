from django.db import models

# Create your models here.
class Users(models.Model):
    username = models.CharField(max_length=50,null=False)
    password = models.CharField(max_length=50,null=False)
    level  = models.CharField(max_length=1,null=False)
    status = models.CharField(max_length=1,null=False)
    def __unicode__(self):
        return self.username

class Projects(models.Model):
    pjCode = models.CharField(max_length=50,null=False)
    pjName = models.CharField(max_length=50,null=False)
    def natural_key(self):
        return (self.pjName)
    def __unicode__(self):
        return self.pjName
    
class Envs(models.Model):
    envCode = models.CharField(max_length=50,null=False)
    envName = models.CharField(max_length=50,null=False)
    def natural_key(self):
        return (self.envName)
    def __unicode__(self):
        return self.envName
   
class Servers(models.Model):
    displayName = models.CharField(max_length=200,null=False)
    ip = models.CharField(max_length=16,null=False)
    port = models.IntegerField()
    loginName = models.CharField(max_length=50,null=False)
    loginPasswd = models.CharField(max_length=128,null=False)
    logDir=models.CharField(max_length=200,null=False)
    pj = models.ForeignKey(Projects)
    env = models.ForeignKey(Envs)

    
