var chatHistory = [];
var url_string = window.location.href;
var cognito_token = url_string.substring(url_string.indexOf("=") + 1,url_string.indexOf("&"));


AWS.config.region = 'us-east-1'; // Region
AWS.config.credentials = new AWS.CognitoIdentityCredentials({
    IdentityPoolId: 'us-east-1:f2b048f4-34d9-4ba5-b750-aeabc2e0a4b9',
	Logins: {
	   'cognito-idp.us-east-1.amazonaws.com/us-east-1_XzKUHccNZ': cognito_token
	}
});

setTimeout(function() {
	if(cognito_token=="" || AWS.config.credentials.sessionToken==""){

		
		var appCilentId = '5gpfvguuu4ltgppg018c3q5kgq';
		var callbackUrl = 'https://sample-102020.s3.amazonaws.com/index.html';
		var domainName = 'https://tirupal.auth.us-east-1.amazoncognito.com';


  redirectWebsite = domainName + '/login?response_type=token&client_id=' + appCilentId + '&redirect_uri=' + callbackUrl ;

  location.href = redirectWebsite;

  console.log(redirectWebsite);


}
}, 2000);



function sendMessageToApi(){


  var inputText = document.getElementById('user-input-message').value.trim().toLowerCase();

  document.getElementById('user-input-message').value = "";

  if(inputText == "") {s
    alert("Please enter some text");
    return false;
  }else {

    chatHistory.push('<b><color = "red" class="user">User:</color> </b>' + inputText);

    document.getElementById('bot-response').innerHTML = "";

    chatHistory.forEach((element) => {
      document.getElementById('bot-response').innerHTML += "<p>" + element + "</p>";
    });

    receiveMessageFromApi(inputText);
    return false;
  }

}

function receiveMessageFromApi(inputText){

	  return AWS.config.credentials.getPromise()
  .then(()=>{


    console.log('Successfully logged!');

    apigClient = apigClientFactory.newClient({
      accessKey: AWS.config.credentials.accessKeyId,
      secretKey: AWS.config.credentials.secretAccessKey,
      sessionToken: AWS.config.credentials.sessionToken
    });

    var params = {};
    var body = {
      "message":inputText,
      "userId":AWS.config.credentials._identityId
    };

    var additionalParams = {
      headers: {
        "x-api-key": "UbK8pC2c8KZmzYOgKfXu7GnuBzUMW3I94mCPnN56",
      },
      queryParams: {}
    };
    return apigClient.chatbotPost(params,body,additionalParams);
 

  })
  .then((result) =>{


      chatHistory.push('<b><color = "Cyan" class="bot">Bot:</color> </b>' + JSON.stringify(result.data.message).replace(/"/g,""));

      document.getElementById('bot-response').innerHTML = "";
      chatHistory.forEach((element) => {
        document.getElementById('bot-response').innerHTML += "<p>" +element + "</p>";
      });
  
  })
  .catch((err) =>{
    console.log(err);
  });

}

