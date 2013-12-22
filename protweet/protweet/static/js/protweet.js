//ProTweet Custom js//

$(document).ready(function() {

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
