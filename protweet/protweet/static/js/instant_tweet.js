//Creating the socket object
var socket = io.connect('localhost', {
	port: 3000
});

socket.on('tweet_feed', function(data) {
	console.log(data);

	//Update the knockout observable to trigger the change in the client
	my.viewModel.ko_push_tweet_feed(JSON.parse(data));
});
