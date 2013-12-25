from django.conf.urls import patterns, url
from core import views

urlpatterns = patterns('',
	url(r'^$', views.protweet_login),
	url(r'^protweet-login/?$', views.protweet_login),
	url(r'^protweet-registration/?$', views.protweet_registration),
	url(r'^home/?$', views.home),
	url(r'^logout/?$', views.user_logout),
	url(r'^followers/?$', views.followers),
	url(r'^following/?$', views.following),
	url(r'^post-tweet/?$', views.post_tweet),
	url(r'^user-tweets/?$', views.user_tweets),
	url(r'^remove-tweet/?$', views.remove_tweet),
	url(r'^follow-user/?$', views.follow_user),
	url(r'^get-user-base/?$', views.get_user_base),
	url(r'^unfollow-user/?$', views.unfollow_user),
	url(r'^follow-user/?$', views.follow_user),
	url(r'^pro-retweet/?$', views.pro_retweet),
	
	url(r'^validate-user/?$', views.validate_user)
)
