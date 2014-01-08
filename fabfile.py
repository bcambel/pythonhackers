from fabric.api import run, sudo, env, task
from fabric.context_managers import cd
import logging
from fabtools import require

# env.hosts = []
setup = {
    'stg': {'dir': '/var/www/stg.pythonhackers.com', 'supervisor': 'staging_pythonhackers'},
    'prd': {'dir': '/var/www/beta.pythonhackers.com', 'supervisor': 'prod_pythonhackers'},
}

env.user = 'root'

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

#"moreutils"

@task
def install_java():
    require.deb.packages(["openjdk-7-jdk", "openjdk-7-jre"], update=True)


@task
def restart_process(setup):
    project = setup['supervisor']
    sudo("supervisorctl restart {}".format(project))


@task
def glog():
    with cd(env.root):
        run("git log -2")


@task
def update_code(settings):
    with cd(settings['dir']):
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
def deploy(settings='stg', restart=False):

    setting = setup[settings]

    update_code(setting)
    logging.warn("Should restart? %s %s" % (restart, bool(restart)))

    if bool(restart):
        restart_process(setting)
        log()


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
def log(directory='/var/log/python/stg.pythonhackers/', tail_file='app.log'):
    with cd(directory):
        run("tail -f {}".format(tail_file))


@task
def nlog():
    with cd("/var/log/nginx/stg.pythonhackers.com"):
        run("tail -f access.log")


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