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
		
		subscribed_tweets_record = get_subscribed_tweets(user_info['userprofile_id'])
		subscribed_tweets = []
		for tweets in subscribed_tweets_record:
			tmp = {}
			user_info_tmp = get_user_details(tweets.tweet_userprofile.user)
			tmp['user_info'] = user_info_tmp
			tmp['tweet'] = tweets.tweet
			tmp['post_timestamp'] = tweets.post_timestamp
			tmp['parent_tweet_id'] = tweets.parent_tweet_id
			subscribed_tweets.append(tmp)

		user_info['home'] = True
		user_info['subscribed_tweets'] = subscribed_tweets
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
	
	
#Tweet Follower - Template Rendering
def followers(request):
	user_info = get_user_details(request.user)
	if not user_info:
		return HttpResponseRedirect('/')
		
	#1. Get the users who follow me
	follower_record_follow_me = get_follower_data(user_info['userprofile_id'])
	print 'These are the users who follow me'
	print follower_record_follow_me
	
	#2. Get all the users who i follow
	follower_record_i_follow = get_following_data(user_info['userprofile_id'])
	print 'These are the users who i follow'
	print follower_record_i_follow
	
	#3. Get the user details who follow me
	follower_tmp = []
	for record in follower_record_follow_me:
		tmp = {}
		user_info_following = get_user_details(record.tweet_follower)
		tmp['user_info'] = user_info_following
		tmp['do_i_follow'] = check_following(follower_record_i_follow, user_info_following['userprofile_id']) #Check if i follow this user
		follower_tmp.append(tmp)
	
	user_info['followers'] = True
	user_info['follower_base'] = follower_tmp
	return render(request, 'followers.html', user_info)
	
	

#Check if i follow the given userprofile_id
def check_following(follower_record_i_follow, userprofile_id):
	for record in follower_record_i_follow:
		if (int(record.tweet_following_id)) == (int(userprofile_id)):
			return True
		else:
			return False

	

#Tweet Following - Template Rendering
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
	user_info['username'] = user_record.username
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



#Follow a User
def follow_user(request):
	following_user_id = request.GET.get('user_id')
	
	try:
		following_userprofile = UserProfile.objects.get(user_id = following_user_id)
		follower_userprofile = UserProfile.objects.get(user = request.user)
		 
		following_userprofile_id = following_userprofile.id
		follower_userprofile_id = follower_userprofile.id
	except Exception, e:
		print e
		
	try:
		followingfollower_record = FollowingFollower(tweet_follower_id = follower_userprofile_id, tweet_following_id = following_userprofile_id)
		followingfollower_record.save()
		
	except Exception, e:
		print e
		return HttpResponse(json.dumps({'status': 'fail'}), mimetype='application/json')
		
	try:
		following_userprofile.follower_count += 1
		following_userprofile.save()
		
		follower_userprofile.following_count += 1
		follower_userprofile.save()
	except Exceptin, e:
		print e
		
	user_info = get_user_details(following_userprofile.user)
	
	response = {
		'status': 'ok',
		'following_count': follower_userprofile.following_count,
		'user_info': user_info
	}
	return HttpResponse(json.dumps(response), mimetype='application/json')


#UnFollow a User
def unfollow_user(request):
	following_user_id = request.GET.get('user_id')
	
	try:
		following_userprofile = UserProfile.objects.get(user_id = following_user_id)
		follower_userprofile = UserProfile.objects.get(user = request.user)
		
		following_userprofile_id = following_userprofile.id
		follower_userprofile_id = follower_userprofile.id
		
	except Exception, e:
		print e
		
	try:
		followingfollower_record = FollowingFollower.objects.filter(tweet_follower_id = int(follower_userprofile_id)).filter(tweet_following_id = following_userprofile_id)
		followingfollower_record.delete()
	except Exception, e:
		print e
		return HttpResponse(json.dumps({'status': 'fail'}), mimetype='application/json')
		
		
	try:
		following_userprofile.follower_count -= 1
		following_userprofile.save()

		follower_userprofile.following_count -= 1
		follower_userprofile.save()

	except Exceptin, e:
		print e
		
	user_info = get_user_details(following_userprofile.user)
	
	response = {
		'status': 'ok',
		'following_count': follower_userprofile.following_count,
		'user_info': user_info
	}
	return HttpResponse(json.dumps(response), mimetype='application/json')
	
	
#Get the follower data
def get_follower_data(userprofile_id):
	try:
		follower_record = FollowingFollower.objects.filter(tweet_following_id = userprofile_id)
	except Exception, e:
		print e
		return None
		
	return follower_record
	
	
#Get the following data
def get_following_data(userprofile_id):
	try:
		print userprofile_id
		following_data = FollowingFollower.objects.filter(tweet_follower_id = userprofile_id)
	except Exception, e:
		print e
		return None
		
	return following_data
	

#Get other users whom are not followed and neither are they following back
def get_user_suggestion(filter_list):
	print filter_list
	suggested_record = UserProfile.objects.all().exclude(id__in=filter_list)
	
	print suggested_record
	
	return suggested_record


#Get user base data for following-follower
def get_user_base(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/')
		
	user_info = get_user_details(request.user)
	follower_record = get_follower_data(user_info['userprofile_id'])
	following_record = get_following_data(user_info['userprofile_id'])
	
	filter_list = []
	filter_list.append(user_info['userprofile_id'])

	#1. Get the users whom i follow
	following_tmp = []
	for record in following_record:
		tmp = {}
		user_info = get_user_details(record.tweet_following)
		tmp['user_info'] = user_info
		filter_list.append(user_info['userprofile_id'])
		following_tmp.append(tmp)
		
	#2. Get the users who follow me
	follower_tmp = []
	for record in follower_record:
		tmp = {}
		user_info = get_user_details(record.tweet_follower)
		tmp['user_info'] = user_info
		filter_list.append(user_info['userprofile_id'])
		follower_tmp.append(tmp)
		
		
	#3. Get all users who i don't follow and they don't follow me as suggestion for potential follows
	suggestion_record = get_user_suggestion(filter_list)
	suggestion_tmp = []
	for record in suggestion_record:
		tmp = {}
		user_info = get_user_details(record.user)
		tmp['user_info'] = user_info
		suggestion_tmp.append(tmp)


	user_base = {}
	user_base['following'] = following_tmp
	user_base['follower'] = follower_tmp
	user_base['suggestion'] = suggestion_tmp
	
	print user_base
	
	response = {
		'status': 'ok',
		'user_base': user_base
	}
	
	return HttpResponse(json.dumps(response), mimetype="application/json")
		
		
		
#Get all the tweets from the user that i am following
def get_subscribed_tweets(userprofile_id):
	#Get all the user profiles that i follow
	following_record = get_following_data(userprofile_id)
	filter_list = []
	
	#1. Get the users whom i follow
	for record in following_record:
		user_info = get_user_details(record.tweet_following)
		filter_list.append(user_info['userprofile_id'])
	
	try:
		tweet_record = Tweet.objects.filter(tweet_userprofile_id__in = filter_list).order_by('-post_timestamp')
	except Exception, e:
		print e
		return None
		
	return tweet_record
	
		