//ProTweet Custom js//
var COUNT_MAX = 200;
var my = {};

$(document).ready(function() {

	//applying knockout binding to our viewmodel
	my = {viewModel: new ko_follower_following_view_model()}
	ko.applyBindings(my.viewModel);

	//tweet word count validator event bindings
	if ($('#tweet-composer').val() != undefined) {
		$('#counter').text($('#tweet-composer').val().length || 0)
	} 
	
	$(document).keyup(function(e){if(e.keyCode == 8)validate_counter(COUNT_MAX);})
	$('#tweet-composer').keyup(function() {
		validate_counter(COUNT_MAX);
	});
	
	//tweet post button click event
	$('.textarea-wrapper button').click(function() {
		var post = $('#tweet-composer').val();
		post_tweet(post);
	});
	
	//redirection on click from li
	$('.sidebar-nav li').click(function() {
		var path = $(this).find('a').attr('href');
		window.location.href = path;
	});	
	
	//removing tweet for the given user
	$('.remove-tweet').click(function(e){
		e.preventDefault();
		var el = $(this);
		var tweet_id = el.attr('data-tweet-id');
		remove_tweet(tweet_id, el);
	});
	
	//follow click event
	$('.protweet-follow').click(function() {
		var user_id = $(this).attr('data-id');
		var el = $(this);
		
		protweet_follow(user_id, el);

	});
	
	//unfollow click event
	$('.protweet-unfollow').click(function() {
		var user_id = $(this).attr('data-id')
		var el = $(this);
		
		protweet_unfollow(user_id, el);
	})
	
	//retweet event
	$('.pro-retweet').click(function(e) {
		e.preventDefault();
		var tweet_id = $(this).attr('data-tweet-id');
		pro_retweet(tweet_id);
	});
});

/*
 *Validating the tweet word count constraint
 */
function validate_counter(max) {
	$('.lbl-thoughts-wrapper > .vs-reg-lbl-error').removeClass('lbl-thoughts-show').addClass('lbl-thoughts-hide');	
	var el = $('#tweet-composer');
	if (el.val().length > max) {
	    el.val(el.val().substring(0, max));
		$('#counter').text(el.val().length);
	} else {
		$('#counter').text(el.val().length);
	}
};

/*
 *Posting the tweet to the server
 */
function post_tweet(post) {
	//Check to see if the post is empty
	if (post == undefined || post == null) {
		$('.lbl-thoughts-wrapper > .vs-reg-lbl-error').removeClass('lbl-thoughts-hide').addClass('lbl-thoughts-show');
		return;
	}
	
	if (post.length == 0) {
		$('.lbl-thoughts-wrapper > .vs-reg-lbl-error').removeClass('lbl-thoughts-hide').addClass('lbl-thoughts-show');
		return;
	}
	
	//Posting the tweet to the server
	$.ajax({
		url: '/post-tweet',
		type: 'GET',
		data: {
			'tweet_post': post
		},
		datatype: 'json',
		success: function(response) {
			if(response.status == 'ok') {
				$('#tweet-composer').val(''); //clearing the tweet textarea
				validate_counter(validate_counter);
				$('#tweet_count').html('(' + response.tweet_count + ')'); //updating the tweet count
				
			} else {
				
			}
		},
		error: function(response) {
		
		}
	});
}


/*
 *Remove tweet, on success clear the tweet from the current page 
 */
function remove_tweet(tweet_id, el) {
	$.ajax({
		url: '/remove-tweet',
		data: {
			'tweet_id': tweet_id
		},
		datatype: 'json',
		success: function(response) {
			if (response.status == 'ok') {
				el.parent().remove(); //removing the tweet from the dom
				$('#tweet_count').html('(' + response.tweet_count + ')'); //updating the tweet count
			} else {
				
			}
		},
		error: function(response) {
			
		}
	});
}


/*
 *Knockout-follower-following
 */

//constructor for the followingfollower base
function ko_following(data) {
	var self = this;

	self.ko_username = ko.observable(data.ko_username);
	self.ko_user_id = ko.observable(data.ko_user_id);
	self.ko_follow_count = ko.observable(data.ko_follow_count)
	self.ko_follower_count = ko.observable(data.ko_follower_count)
	self.ko_tweet_count = ko.observable(data.ko_tweet_count)
}

//knockout view model
function ko_follower_following_view_model() {
	self = this;
	
	self.ko_follower_base = ko.observableArray([]); //Holds all the users that follow me
	self.ko_following_base = ko.observableArray([]); //Holds all the users that i follow
	self.ko_suggestion_base = ko.observableArray([]); //This is the list of users that i can follow

	//Properties of each user
	self.ko_username = ko.observable();
	self.ko_user_id = ko.observable();
	self.ko_follow_count = ko.observable();
	self.ko_follower_count = ko.observable();
	self.ko_tweet_count = ko.observable();

	self.ko_follow_user = function(user_index, el) {
		var user_id = $(el).attr('data-id');
		console.log('Follow User');
		console.log(user_id);
		$.ajax({
			url: '/follow-user',
			data: {
				'user_id': user_id
			},
			datatype: 'json',
			success: function(response) {
				if (response.status == 'ok') {
					var new_html = 'Unfollow';
					$('#following_count').html('(' + response.following_count + ')');
					
					console.log(JSON.stringify(response));

					self.ko_following_base.push(new ko_following({
						ko_username: response.user_info.username,
						ko_user_id: response.user_info.user_id,
						ko_follow_count: response.user_info.following_count,
						ko_follower_count: response.user_info.follower_count,
						ko_tweet_count: response.user_info.tweet_count
					}));
					
					self.ko_suggestion_base.splice(user_index, 1);
					
				}
			},
			error: function(response) {

			}
		});

	}
	
	//Unfollowing the user
	self.ko_unfollow_user = function(user_index, el) {
		var user_id = $(el).attr('data-id');
		$.ajax({
			url: '/unfollow-user',
			data: {
				'user_id': user_id
			},
			datatype: 'json',
			success: function(response) {
				if (response.status == 'ok') {
					self.ko_following_base.splice(user_index, 1);
					
					$('#following_count').html('(' + response.following_count + ')');
					
					console.log(JSON.stringify(response));
					
					self.ko_suggestion_base.push(new ko_following({
						ko_username: response.user_info.username,
						ko_user_id: response.user_info.user_id,
						ko_follow_count: response.user_info.following_count,
						ko_follower_count: response.user_info.follower_count,
						ko_tweet_count: response.user_info.tweet_count
					}));
				}
			},
			error: function(response) {
				
			}
		});
		
	}

	//Loading the initial set of data from the server
	self.ko_initialize = function(base) {
		$.ajax({
			url: '/get-user-base',
			success: function(response) {
				if (response.status == 'ok') {
					
					if (base == 'following_base') {
						//1. Populating ko_following_base
						response.user_base.following.forEach(function(user) {

							self.ko_following_base.push(new ko_following({
								ko_username: user.user_info.username,
								ko_user_id: user.user_info.user_id,
								ko_follow_count: user.user_info.following_count,
								ko_follower_count: user.user_info.follower_count,
								ko_tweet_count: user.user_info.tweet_count
							}));
						});
						
						//2. Populating ko_suggestion_base
						response.user_base.suggestion.forEach(function(user) {

							self.ko_suggestion_base.push(new ko_following({
								ko_username: user.user_info.username,
								ko_user_id: user.user_info.user_id,
								ko_follow_count: user.user_info.following_count,
								ko_follower_count: user.user_info.follower_count,
								ko_tweet_count: user.user_info.tweet_count
							}));
						});
						
					}
					
				} else {
					
				}
			},
			error: function(response) {
				
			}
		});
	}
}


/*
 *Document onload event for the Following template
 */
function init_following() {
	$('#trigger_following_base').click();
	my.viewModel.ko_initialize('following_base');
}


/*
 *Following a user
 */
function protweet_follow(user_id, el) {
	$.ajax({
		url: '/follow-user',
		data: {
			'user_id': user_id
		},
		datatype: 'json',
		success: function(response) {
			if (response.status == 'ok') {
				//'<span class="glyphicon glyphicon-ban-circle"></span>
				var new_html = 'Unfollow';
				el.html(new_html);
				el.removeClass('protweet-follow').addClass('protweet-unfollow');
				
				$('#following_count').html('(' + response.following_count + ')');
			}
		},
		error: function(response) {
			
		}
	});
}


/*
 *Unfollow a user
 */
function protweet_unfollow(user_id, el) {
	$.ajax({
		url: '/unfollow-user',
		data: {
			'user_id': user_id
		},
		datatype: 'json',
		success: function(response) {
			if (response.status == 'ok') {
				//<span class="glyphicon glyphicon-ban-circle"></span>
				var new_html = 'Follow';
				el.html(new_html);
				el.removeClass('protweet-unfollow').addClass('protweet-follow');
				
				$('#following_count').html('(' + response.following_count + ')');
			}
		},
		error: function(response) {
			
		}
	});	
}


/*
 *Retweeting the tweet
 */
function pro_retweet(tweet_id) {
	$.ajax({
		url: '/pro-retweet',
		data: {
			'tweet_id': tweet_id
		},
		datatype: 'json',
		success: function(response) {
			if (response.status == 'ok') {
				$('#tweet_count').html('(' + response.tweet_count + ')');
			}
		},
		error: function(response) {
			
		}
	});
}
