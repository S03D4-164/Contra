# Contra
Contents Tracker

This is a tool for getting contents and screenshots of web pages, and viewing it from Web UI.

## Quick Start
### Requirements
    $ sudo aptitude install postgresql redis-server libfuzzy-dev
Also, you must install Docker. Please refer "Install Docker Engine" on Docker official.

### Setup Environment
    $ virtualenv venv && cd venv
    $ source bin/activate
    $ pip install django psycopg2 requests umsgpack celery[redis] tldextract sh python-Wappalyzer pythonwhois ipwhois chardet python-magic ssdeep Pillow django_datatables_view docker-py
    $ django-admin startproject myproject && cd myproject
    $ git clone http://github.com/S03D4-164/Contra
    
    Edit myproject/settings.py
    1. Add following to INSTALLED_APPS:
    'Contra.frontend',
    'Contra.backend',
    2. Change ROOT_URLCONF to 'Contra.urls'
    3. Edit DATABASES (postgresql is recommended)
    eg.
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': <db name>,
    'USER': <db user name>,
    'PASSWORD': <db password>,
    
    $ sh Contra/createdb.sh (Please edit the script to be suitable for your environment.)
  
### Create Docker
    $ cd Contra/backend/docker
    $ sh build.sh (This will take a long time)

### Run
    Run following in project directory (I think I should use Supervisor...)
    $ celery worker -A Contra.frontend -l info -d
    $ celery worker -A Contra.backend -l info -d
    $ python manage.py runserver
