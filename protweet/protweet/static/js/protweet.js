//ProTweet Custom js//

$(document).ready(function() {

	//applying knockout binding to our viewmodel
	my = {viewModel: new ko_follower_following_view_model()}
	ko.applyBindings(my.viewModel);

	//tweet word count validator event bindings
	if ($('#tweet-composer').val() != undefined) {
		$('#counter').text($('#tweet-composer').val().length || 0)
	} 
	
	$(document).keyup(function(e){if(e.keyCode == 8)validate_counter(200);})
	$('#tweet-composer').keyup(function() {
		validate_counter(200);
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
	
	$('.protweet-follow').click(function() {
		var user_id = $(this).attr('data-id');
		var el = $(this);
		
		protweet_follow(user_id, el);

	});
	
	$('.protweet-unfollow').click(function() {
		var user_id = $(this).attr('data-id')
		var el = $(this);
		
		protweet_unfollow(user_id, el);
	})
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
				validate_counter(200);
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

//constructor for the following base
function ko_following(data) {
	var self = this;

	self.ko_username = ko.observable(data.ko_username);
	self.ko_user_id = ko.observable(data.ko_user_id);
}

//constructor for the follower base
function ko_follower(data) {
	var self = this;
	
	self.ko_username = ko.observable(data.ko_username);
	self.ko_user_id = ko-observable(data.ko_user_id);
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

	self.ko_follow_user = function(el) {
		var user_id = $(el).attr('data-id');
		console.log('Follow Th User');
		// $.ajax({
		// 	type: 'GET',
		// 	url: '/follow-user',
		// 	data: {
		// 		'user_id': ko_user_id
		// 	},
		// 	success: function(data) {
		// 		//Adding fields into ko_follow_base
		// 		self.ko_follow_base.push(new ko_follow({
		// 				ko_username: ko_username, 
		// 				ko_user_id: ko_user_id
		// 			}
		// 		));
		// 	},
		// 	error: function(data) {
		// 		// alert('FAILS');
		// 	}
		// });
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
				}
			},
			error: function(response) {
				
			}
		});
		
	}

	//Loading the initial set of data from the server
	self.ko_initialize = function(el, base) {
		$.ajax({
			url: '/get-user-base',
			success: function(response) {
				if (response.status == 'ok') {
					
					if (base == 'following_base') {
						//1. Populating ko_following_base
						response.user_base.following.forEach(function(user) {
							var username = user.user_info.username;
							var user_id = user.user_info.user_id;

							self.ko_following_base.push(new ko_following({
								ko_username: username,
								ko_user_id: user_id
							}));
						});
						
						//2. Populating ko_suggestion_base
						
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
				var new_html = '<span class="glyphicon glyphicon-ban-circle"></span>Unfollow';
				el.html(new_html);
				el.removeClass('protweet-follow').addClass('protweet-unfollow');
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
				var new_html = '<span class="glyphicon glyphicon-ban-circle"></span>Follow';
				el.html(new_html);
				el.removeClass('protweet-unfollow').addClass('protweet-follow');
			}
		},
		error: function(response) {
			
		}
	});	
}