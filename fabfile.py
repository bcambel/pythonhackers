from fabric.api import run, sudo, env, task
from fabric.context_managers import cd
import logging

env.hosts = ['pyhackers']
env.root = '/var/www/pythonhackers.com/'
env.user = 'root'
env.key_filename = '~/.ssh/digital'


@task
def restart_nginx():
    run("service nginx restart")


@task
def restart_process():
    sudo("supervisorctl restart pythonhackers")


@task
def glog():
    with cd(env.root):
        run("git log -2")


@task
def update_code():
    with cd(env.root):
        run("git pull")


@task
def install(*packages):
    assert packages is not None
    sudo("apt-get -y install %s" % packages)


@task
def deploy(restart=False):
    update_code()
    logging.warn("Should restart? %s %s" % (restart, bool(restart)))
    if bool(restart):
        restart_process()


@task
def super(mode=""):
    sudo("supervisorctl %s" % mode)


@task
def hostname_check():
    run("hostname")


@task
def disc_status():
    run("df -h")

@task
def nlog():
    with cd("/var/log/nginx/stg.pythonhackers.com"):
        run("tail -100 access.log")