from fabric.api import *
from fabric.context_managers import cd

env.hosts = ['pyhackers']
env.root = '/var/www/pythonhackers.com/'
env.user = 'root'


def restart_nginx():
    run("/service nginx restart")


def restart_processes():
    sudo("supervisorctl restart pythonhackers")


def show_git_log():
    with cd(env.root):
        run("git log -2")


def update_code():
    with cd(env.root):
        run("git pull")


def install(package=None):
    assert package is not None
    sudo("apt-get -y install %s" % package)


def get_latest_release():
    update_code()
    restart_nginx()


def super(mode=""):
    sudo("supervisorctl %s" % mode)


def hostname_check():
    run("hostname")


def disc_status():
    run("df -h")

