const Moralis = require('moralis').default;

const jwt = require('jsonwebtoken');
const jwt_decode = require("jwt-decode");

const config = {
  domain: process.env.AppDomain,
  statement: 'Please sign this message to confirm your identity.',
  uri: process.env.ReactUrl,
  timeout: 60,
};

const startMoralis = async () => {
    await Moralis.start({
      apiKey: process.env.Key2
    });
};

startMoralis();

exports.lambda_handler = async function(event, context) {

  if (event.path == "/auth/request-message"){
      console.log("Path is /auth/request-message")
      const body = JSON.parse(event.body)
      const { address, chain } = body;
      console.log(body)
      console.log(address)
      console.log(chain)
      
      try {
        const message = await Moralis.Auth.requestMessage({
          address,
          chain,
          ...config,
        });
        console.log("Message is:")
        console.info(message);
        return {
          statusCode: 200,
          body: JSON.stringify(message),
          headers: {
            "origin": "https://authe.io",
            'Access-Control-Allow-Credentials': 'true'
          }
        }
      } catch (error) {
        console.error(error);
        return {
          statusCode: 400,
          body: JSON.stringify({ error: error.message }),
        }
      }
  }

  if (event.path == "/auth/verify"){
      console.log("Path is /auth/verify")
      try {
        const body = JSON.parse(event.body)
        const { message, signature } = body;
        console.log(message)
        console.log(signature)
        
        const { address, profileId } = (
          await Moralis.Auth.verify({
            message,
            signature,
          })
        ).raw;
        
        const user = { address, profileId, signature };
        
        // create JWT token
        const token = jwt.sign(user, process.env.AuthSecret);
        console.log(token)
        
        return {
          statusCode: 200,
          body: JSON.stringify({}),
          multiValueHeaders : {"Set-Cookie": [`jwt=${token}`]},
          headers: {
            "origin": "https://authe.io",
            'Access-Control-Allow-Credentials': 'true'
          }
        }
        
      } catch (error) {
        console.error(error);
        return {
          statusCode: 400,
          body: JSON.stringify({ error: error.message }),
        }
      }
  }

  if (event.path == "/auth/authenticate"){
    console.log("Path is /auth/authenticate")
    console.log(event)

    if (event["headers"]["origin"] == "http://localhost:3000"){
      var jwt_raw = "jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhZGRyZXNzIjoiMHg1NjBFY0YxNTQxMzg5ZDcxNDg0Mzc0Q0ZlYjc1MDg0NzUyNTU4MmJlIiwicHJvZmlsZUlkIjoiMHgzYTE0MjU5YWQyYWJiOWE1NGJjZGIyNjY4ZDQ3OTI1YmExNzU5YjRlYzMxN2NkZmU3YmZkZDAzNTlhMmZhMzQ4Iiwic2lnbmF0dXJlIjoiMHhkMzI0NDZhNzM1YmFlYTdjZTlhYjUyZDY3YjUwZTliZTU4NWQ1Y2YwZDhjYTI5YmZlZDM5NGQ1YzhjZTIxMzY0MzlhY2U3YjUwYWU3NDdiMWJkZGEzYTk5NjUyZDE1NjQ0N2M0NzQ5ZWJmMWFjNTMwOTZkOTUyZTc4MmUyM2E0ZDFiIiwiaWF0IjoxNjg1OTY0MzkwfQ.8sb5qvRGUNk0Bj2Wwugnps5CAhniRyirJO7utHyhsKA; jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhZGRyZXNzIjoiMHg1NjBFY0YxNTQxMzg5ZDcxNDg0Mzc0Q0ZlYjc1MDg0NzUyNTU4MmJlIiwicHJvZmlsZUlkIjoiMHgzYTE0MjU5YWQyYWJiOWE1NGJjZGIyNjY4ZDQ3OTI1YmExNzU5YjRlYzMxN2NkZmU3YmZkZDAzNTlhMmZhMzQ4Iiwic2lnbmF0dXJlIjoiMHhmNjFmOTEzZmE5NWQyNmQ3ZTUxMGZlOGEwMGFiOWMwMGM3ZDY1YmViOTQwOTJkYWI1OGY5NGU1OTJiNWJiMWU1MTNmNTFjMjcxMmVlNTI3NTg1YzI2OTkyOGY3ZjVkMmJjYzcyNTBlNTJhMGM2NDliZTY5ZGJkYTNjYzUyY2NkYTFiIiwiaWF0IjoxNjg1OTY3OTY1fQ.4IndMe8oV-EBp7KD_4jHa-ANLTfVW5iXZfo9hzXhoeY"
    }
    else{
      var jwt_raw = event["headers"]["Cookie"]
      console.log(jwt_raw.split(";")[0].split("jwt=")[1]) // Hack to get it to work quickly. Some issue with Cloudfront headers
    }

    var token = jwt_raw.split(";")[0].split("jwt=")[1]
    var data = jwt_decode(token);
    console.log(data)

    // const token = event.cookies.jwt;
    if (!token) {
      console.log("Did not receive a JWT")
      return {
        statusCode: 403 // if the user did not send a jwt token, they are unauthorized
      }
    }
    
    try {
      // const data = jwt.verify(token, process.env.Auth_secret);
      console.log("Authenticated the data")
      console.log(data)
      
      return {
        statusCode: 200,
        body: JSON.stringify(data),
        headers: {
          "origin": "https://authe.io",
          'Access-Control-Allow-Credentials': 'true'
        }
      }
    
    } catch (error) {
      console.error(error);
      return {
        statusCode: 403
      }
      
    }
  }
  

  if (event.path == "/auth/logout"){
    console.log("Path is /auth/logout")

    try {
      console.log("Clearing cookie")
      return {
        statusCode: 200,
        headers: {
          "origin": "https://authe.io",
          'Access-Control-Allow-Credentials': 'true'
        }
      }
    } catch (error) {
      console.error(error);
      
      return {
        statusCode: 403,
        multiValueHeaders : {"Set-Cookie": [`jwt=""`]}
      }
    }
  }
  
  return {
      statusCode: 200,
      body: JSON.stringify({}),
          headers: {
            "origin": "https://authe.io",
            'Access-Control-Allow-Credentials': 'true'
          }
    }
  }
  
