protweet - A twitter prototype built with python django.
Author: Binay Budhathoki - binay.b@gmail.com


Installation
------------

This installation assumes you have python and pip pre-installed on your system. If not install those first.

1) Install Virtual Environment - Refer to help link 2
2) mkdir env
3) virtualenv env
4) source env/bin/activate
5) pip install -r requirements.pip

6) setting up mysql database
	-create database `protweet`
	-grant all privileges on `protweet`.* to `protweet`@`localhost` identified
	     by 'abc123';

7) python manage.py syncdb
8) python manage.py migrate


The following links maybe helpful to bootstrap the project
1)http://www.jeffknupp.com/blog/2012/02/09/starting-a-django-project-the-right-way/
2)http://dabapps.com/blog/introduction-to-pip-and-virtualenv-python/


To run the server
python manage.py runserver


