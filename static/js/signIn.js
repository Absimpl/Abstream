$(function(){
	$('#btnSignIn').click(function(){
		
		$.ajax({
			url: '/signIn',
			data: $('form').serialize(),
			type: 'POST',
			success: function(response){
				console.log(response);
			if(response == 'ok'){
                        //$('#resp2').load('../templates/viewstream7.html');
		        $("#resp2").html("Account verified successfully, please click View events");
			}
			 
			if(response == 'nok'){
				$("#resp2").html("Account verification failed!!");
				
				}
			$("#resp2").show();
			},
			error: function(error){
				console.log(error);				
				
			}
		});
	});
});
