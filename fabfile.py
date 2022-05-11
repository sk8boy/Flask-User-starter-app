# Definition file for Fabric -- an SSH command-line tool

from fabric.api import task
from fabric.operations import local


@task
def runserver():
    local('python manage.py runserver')


@task
def test():
    local('py.test tests/')


@task
def test_cov():
    local('py.test -s --cov-report term-missing --cov-config tests/.coveragerc --cov app tests/')


@task
def tox():
    local('tox')
