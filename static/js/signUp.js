$(function(){
	$('#btnSignUp').click(function(){
		
		$.ajax({
			url: '/signUp',
			data: $('form').serialize(),
			type: 'POST',
			success: function(response){
				console.log(response);
			if(response == 'ok'){
			$("#resp1").html("Account created successfully, please click View events");
			}
			 
			if(response == 'nok'){
				$("#resp1").html("Please fill the details!!!");
				
				}
			$("#resp1").show();
			},
			error: function(error){
				console.log(error)				
			}
		});
	});
});
