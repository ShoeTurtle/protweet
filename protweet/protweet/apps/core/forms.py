import datetime
from django import forms
from core.models import UserProfile, Tweet, FollowingFollower, User
from django.contrib.auth import authenticate, login


#Registration Form
class ProTweetRegistrationForm(forms.Form):
	
	def clean(self):
		cleaned_data = super(ProTweetRegistrationForm, self).clean()
		pt_form_keys = cleaned_data.keys()
		
		if 'tweet_handle' in pt_form_keys:
			tweet_handle = cleaned_data.get('tweet_handle').lower()
			if User.objects.filter(username__iexact = tweet_handle.lower()):
				raise forms.ValidationError("The handle is already registered with us.")

		if 'password' in pt_form_keys and 're_password' in pt_form_keys:
			if cmp(cleaned_data.get("password"), cleaned_data.get("re_password")):
				raise forms.ValidationError("Passwords do not match.")

		return cleaned_data

	name = forms.CharField(max_length = 100, widget = forms.TextInput({"placeholder": "Name"}), required = True)
	tweet_handle = forms.CharField(max_length = 100, widget = forms.TextInput({"placeholder": "Tweet Handle"}), required = True)
	email = forms.EmailField(max_length = 100, widget = forms.TextInput({ "placeholder": "Email"}), required = True)
	password = forms.CharField(max_length = 100, widget = forms.PasswordInput({ "placeholder": "Enter Password"}), required = True)
	re_password = forms.CharField(max_length = 100, widget = forms.PasswordInput({ "placeholder": "Confirm Password"}), required = True)
	
	
#Login Form
class ProTweetLoginForm(forms.Form):

	def clean(self):
		cleaned_data = super(ProTweetLoginForm, self).clean()
		username = cleaned_data.get("tweet_handle")
		password = cleaned_data.get("password")
		user = authenticate(username=username, password=password)
		if user is None:
			raise forms.ValidationError("Invalid username or password.")

		return cleaned_data


	tweet_handle = forms.CharField(max_length = 100, widget = forms.TextInput({"placeholder": "Tweet Handle"}), required = True)
	password = forms.CharField(max_length = 100, widget = forms.PasswordInput({ "placeholder": "Enter Password"}), required = True)