import datetime, base64
import simplejson as json
import requests, urllib
import json, re, uuid
import smtplib, os

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic.base import View
from django.contrib.auth.models import User
from urlparse import urlparse
from django.contrib.auth import authenticate, login, logout
from django.core.files import File
from django.db.models import Count
# from django.conf import settings

from core.models import UserProfile, Tweet, FollowingFollower
from core.forms import ProTweetLoginForm, ProTweetRegistrationForm


#ProTwitter Home
def home(request):
	user_info = {}
	if request.user.is_authenticated():
		print request.user
		try:
			user_record = User.objects.get(username = request.user)
		except Exception, e:
			print 'Unable to query User'
			print e
			return HttpResponseRedirect('/')

		user_info['username'] = request.user
		user_info['name'] = user_record.first_name
		
		return render(request, 'home.html', user_info)
	
	return HttpResponseRedirect('/')
	

#Login View
def protweet_login(request):
	if request.method == 'POST':
		form = ProTweetLoginForm(request.POST)
		msg = {'form': form}
		if form.is_valid():
			correct_data = form.cleaned_data
			username = correct_data['tweet_handle']
			password = correct_data['password']
			user = authenticate(username=username, password=password)
			login(request, user)
			
			return HttpResponseRedirect('/home')
		else:
			context = {'form': form}
	else:
		if request.user.is_authenticated():
			return HttpResponseRedirect('/home')
		
		form = ProTweetLoginForm()
		context = {'form': form}

	return render(request, 'login.html', context)
	

#Logout
def user_logout(request):
	print 'Loggin out'
	logout(request)
	return HttpResponseRedirect('/')
	
	
#Registration View
def protweet_registration(request):
	if request.method == "POST":
		form = ProTweetRegistrationForm(request.POST)
		msg = {'form': form}
		if form.is_valid():
			correct_data = form.cleaned_data
			#1. Creating the User
			try:
				user = User.objects.create_user (
					username = correct_data['tweet_handle'].lower(),
					first_name = correct_data['name'],
					last_name = 'none',
					email = correct_data['email']
				)
				
				user.set_password(correct_data['password'])
				user.save()
				
			except Exception, e:
				print 'Unable to Create User'
				print e
				return HttpResponseRedirect('/')
			
			#2. Initializing UserProfile
			try:
				user_profile = UserProfile(user = user)
				user_profile.save()
			except Exception, e:
				print 'Unable to Initialize UserProfile'
				print e
				#ToDo: Clear the previous failed user from db
				return HttpResponseRedirect('/')
				
			#3. Authentication User
			username = correct_data.get('tweet_handle')
			password = correct_data.get('password')
			
			user = authenticate(username = username, password = password)

			#5. Loggin in the user
			login(request, user)
			
			return HttpResponseRedirect('/home')
			
		else:
			context = {'form': form}
	else:
		form = ProTweetRegistrationForm()
		context = {'form': form}
		
	return render(request, 'register.html', context)