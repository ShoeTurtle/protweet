from django.db import models
from django.contrib.auth.models import User


#UserProfile Model
class UserProfile(models.Model):
	user = models.ForeignKey(User, related_name = 'user', db_index = True)
	follower_count = models.IntegerField(default = 0)
	following_count = models.IntegerField(default = 0)
	tweet_count = models.IntegerField(default = 0)
	user_creation_timestamp = models.DateTimeField(auto_now = False, auto_now_add = True, editable = False)
	profile_pic = models.ImageField(upload_to = 'profile_pic', blank = True, default = '')
	
	def __unicode__(self):
		return u'%s' % (self.user)

#Tweet Model
class Tweet(models.Model):
	tweet_userprofile = models.ForeignKey(UserProfile, related_name = 'tweet_userprofile', db_index = True)
	parent_tweet_id = models.IntegerField(null = True, blank = True)
	tweet = models.TextField(blank = False, null = False)
	post_timestamp = models.DateTimeField(auto_now = False, auto_now_add = True, editable = False)
	
	def __unicide__(self):
		return u'%s' % (self.tweet_userprofile)

#Following_Follower Model
class FollowingFollower(models.Model):
	tweet_follower = models.ForeignKey(UserProfile, related_name = 'tweet_follower', db_index = True)
	tweet_following = models.ForeignKey(UserProfile, related_name = 'tweet_following', db_index = True)
	
	def __unicode__(self):
		return u'%s - %s' % (self.tweet_follower, self.tweet_following)
	
	
