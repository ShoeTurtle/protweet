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

		user_info = get_user_details(request.user)
		if not user_info:
			return HttpResponseRedirect('/')
		
		user_info['home'] = True
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
				#ToDo: Remove the previous failed user from db
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
	
	
#Tweet Follower
def followers(request):
	user_info = get_user_details(request.user)
	if not user_info:
		return HttpResponseRedirect('/')
	
	user_info['followers'] = True
	return render(request, 'followers.html', user_info)
	
	
#Tweet Following
def following(request):

	user_info = get_user_details(request.user)
	if not user_info:
		return HttpResponseRedirect('/')
	
	user_info['following'] = True
	return render(request, 'following.html', user_info)
	

#Adding tweet to the database
def post_tweet(request):
	post = request.GET.get('tweet_post')
	if len(post) > 200:
		return HttpResponse({'status': 'fail'}, mimetype='application/json')
	
	#1. Insert the post into the database
	try:
		user_id = User.objects.get(username = request.user).id
	except Exception, e:
		print e
		return HttpResponse({'status': 'fail'}, mimetype='application/json')
		
	try:
		userprofile_record = UserProfile.objects.get(user_id = user_id)
	except Exception, e:
		print e
		return HttpResponse({'status': 'fail'}, mimetype='application/json')
		
	try:
		tweet_record = Tweet(tweet_userprofile_id = userprofile_record.id, parent_tweet_id = None, tweet = post)
		tweet_record.save()
	except Exception, e:
		print e
		
	#2. Increment the tweet count
	new_tweet_count = int(userprofile_record.tweet_count) + 1
	userprofile_record.tweet_count = new_tweet_count
	try:
		userprofile_record.save()
	except Exception, e:
		print e
	
	response = {
		'status': 'ok',
		'tweet_count': new_tweet_count
	}
	return HttpResponse(json.dumps(response), mimetype='application/json')
	
	
	
#Get the user details
def get_user_details(username):
	try:
		user_record = User.objects.get(username = username)
	except Exception, e:
		print 'Unable to query User'
		print e
		return None
		
	try:
		userprofile_record = UserProfile.objects.get(user_id = user_record.id)
	except Exception, e:
		print 'Unable to query UserProfile'
		print e
		return None

	#building the user_info
	user_info = {}
	user_info['user_id'] = user_record.id
	user_info['username'] = username
	user_info['name'] = user_record.first_name
	user_info['email'] = user_record.email
	user_info['userprofile_id'] = userprofile_record.id
	user_info['tweet_count'] = userprofile_record.tweet_count
	user_info['follower_count'] = userprofile_record.follower_count
	user_info['following_count'] = userprofile_record.following_count
	
	return user_info
	
	
#Render all the user_tweets
def user_tweets(request):
	user_info = get_user_details(request.user)
	
	if not user_info:
		return HttpResponseRedirect('/')
		
	#Query all the tweet for this user
	try:
		tweet_record = Tweet.objects.values('id', 'parent_tweet_id', 'tweet', 'post_timestamp').filter(tweet_userprofile_id = user_info['userprofile_id']).order_by('-post_timestamp')
	except Exception, e:
		print e

	user_info['user_tweet'] = tweet_record
	
	print user_info
	
	user_info['user_tweets'] = True
	return render(request, 'user_tweets.html', user_info)
	
	
#Removing tweet from the database
def remove_tweet(request):
	tweet_id = request.GET.get('tweet_id')
	
	try:
		tweet_record = Tweet.objects.get(id = tweet_id)
		tweet_record.delete()
		response = {'status': 'ok'}
	except Exception, e:
		print e
		response = {'status': 'fail'}
		
	try:
		userprofile_record = UserProfile.objects.get(user = request.user)
		userprofile_record.tweet_count -= 1
		userprofile_record.save()
		response['tweet_count'] = userprofile_record.tweet_count
	except Exception, e:
		print e
		
		
	return HttpResponse(json.dumps(response), mimetype='application/json')
	