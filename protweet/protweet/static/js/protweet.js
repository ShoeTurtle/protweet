$(document).ready(function() {

	//tweet word count validator event bindings
	$('#counter').text($('#tweet-composer').val().length);
	$(document).keyup(function(e){if(e.keyCode == 8)validate_counter(200);})
	$('#tweet-composer').keyup(function() {
		validate_counter(200);
	});
	
	//tweet post button click event
	$('.textarea-wrapper button').click(function() {
		var post = $('#tweet-composer').val();
		post_tweet(post);
	});
});

/*
 *Validating the tweet word count constraint
 */
function validate_counter(max) {
	el = $('#tweet-composer');
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
	$.ajax({
		url: '/post-tweet',
		type: 'GET',
		data: {
			'tweet_post': post
		},
		datatype: 'json',
		success: function(response) {
			console.log(response);
			if(response.status == 'ok') {
				console.log('Post Received Successful');
				$('#tweet-composer').val('');
				validate_counter(200);
			} else {
				
			}
		},
		error: function(response) {
		
		}
	});
}