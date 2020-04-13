# Blockchain toy example
simple example of blockchain with lightway flask API

## Start the server
from shell
```
python flask_api.py
```
## Interact with the blockchain
examples sending GET and POST requests using curl
following a explanation of the used curl parameters:
* -i Includes the  HTTP  response headers in the output. The HTTP response headers can include things  like  server  name,  cookies, date of the document, HTTP version and more...
* -X (HTTP) Specifies a custom request method to use when communicating  with the HTTP server.  The specified request method will be used instead of the method otherwise  used  (which  defaults  to GET). 
* -H (HTTP)  Extra header to include in the request when sending HTTP to a server.
* -d (HTTP) Sends the specified data in a POST request  to  the  HTTP server,  in  the  same  way  that a browser does when a user has filled in an HTML form and presses the submit button. This  will cause curl to pass the data to the server using the content-type application/x-www-form-urlencoded. (this can be specified through -H)

These examples assume that the server is up on localhost port 5000

### querying for current chain in node
returns current chain
```
curl -i -X GET http://0.0.0.0:5000/chain
```

### mining from current node
returns mined node
```
curl -i -X GET http://0.0.0.0:5000/mine
```

### posting new transaction
```
curl -i -X POST -H "Content-Type: application/json" -d '{"sender": "3f7753513afb4f589718b4c4a6a888a0", "recipient": "some-other-address", "amount":3}' http://0.0.0.0:5000/transactions/new
```