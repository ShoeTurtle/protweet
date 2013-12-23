protweet - A twitter prototype built with python django. <br>
Author: Binay Budhathoki - binay.b@gmail.com


Installation
------------

 This installation assumes you have python and pip pre-installed on your system. If not install those first.

 1) Install Virtual Environment - Refer to help link 2 <br>
 2) mkdir env <br>
 3) virtualenv env <br>
 4) source env/bin/activate <br>
 5) pip install -r requirements.pip <br>

 6) setting up mysql database <br>
	-create database `protweet` <br>
	-grant all privileges on `protweet`.* to `protweet`@`localhost` identified by 'abc123';

 7) python manage.py syncdb <br>
 8) python manage.py migrate <br>


 The following links maybe helpful to bootstrap the project <br> 
 1)http://www.jeffknupp.com/blog/2012/02/09/starting-a-django-project-the-right-way/ <br>
 2)http://dabapps.com/blog/introduction-to-pip-and-virtualenv-python/ <br>


 To run the server <br>
 python manage.py runserver  <br>


