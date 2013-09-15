from fabric.api import run, sudo, env, task
from fabric.context_managers import cd
import logging
from fabtools import require

# env.hosts = []
env.root = '/var/www/pythonhackers.com/'
# env.user = 'root'
env.key_filename = '~/.ssh/digital'

PACKAGES = [
    'supervisor', 'vim', 'htop', 'build-essential',
    'postgresql-9.1', 'memcached', 'libpq-dev',
    'git-core', 'tig', 'redis-server',
    'postgresql-contrib-9.1', 'postgresql-client-9.1',
    'python-pip',
]
# 'newrelic-sysmond'
@task
def install_packages():
    require.deb.package(PACKAGES)

@task
def venv():
    run("pip install virtualenv")

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


# @task
# def install(*packages):
#     assert packages is not None
#     sudo("apt-get -y install %s" % packages)


@task
def ntp():
    require.deb.packages(["ntp"], update=True)
    sudo("service ntp restart")


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


@task
def rabbitmq():
    require.deb.packages(["rabbitmq-server"], update=True)
    sudo("service rabbitmq-server restart")


@task
def redis():
    require.deb.packages(["redis-server"], update=True)
    sudo("service redis-server restart")


@task
def adduser(username, password, pubkey):
    require.user(username,
                 password=password,
                 ssh_public_keys=pubkey,
                 shell="/bin/bash")
    require.sudoer(username)