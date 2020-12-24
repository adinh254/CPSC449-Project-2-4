# CPSC449 - Project2
# Authors: 
Mauricio Macias (mauricio.macias@csu.fullerton.edu) 890741622 <br/>
Ariosto Kuit 	(Ariostokuitak@csu.fullerton.edu) 889834065 <br/>
Andrew Dinh	(decayingapple@csu.fullerton.edu) 893242255 <br/>


## 0 Installation
Make sure you are in the project root and run:

"foreman start"

To run both microservice processes.

## 1 Background 

For this project we build two back-end microservices with Flask for a microblogging service similar to Twitter. 

This project was completed by 3 people. Whose names are listed in the very top of this paper.

For this assignment we are tasked to write two separate Flask application(microservies) to a singe SQLite Version 3 database. The first microservice will be called "User" where it will be task to create a user, authenticate user, add a follower, and remove a follower. The second microservice will be called "Timeslines" where it get the users timeline, get the everyones timeline, get followers timeline, and post tweets.

## 2 Database
We used SQLITE3 as our main database as assigned in the project. We created a file called ‘schema.sql’, which holds all of our tables for each microservices. The sql file contains 3 tables: user, user_relations, and timeline. The file includes a foreign key for the user timeline to access the other tables. The user table includes an integer called ‘id’ which is also a primary key, a unique text or string called ‘username’, a unique text called ‘email’, and a text called ‘password’.

The user_relations table includes an id variable similar to the user table, two integers called ‘follower’ and ‘following’, and a unique(follower, following). Finally the timeline table includes an integer ‘id’ similar to the user table, an integer called ‘user_id’, a timestamp called ‘time_stamp’ and a text called ‘tweet’. After initializing the tables, the file then inserts the user table with values for username, email, and password variables.


## 3 Test Cases

THESE ARE THE COMMANDS TO TEST AND USE RIGHT AFTER YOU RUN OUR PROGRAM

// project 4

start program
foreman start -m "gateway=1,users=3,timelines=3"

remove all flask process: 
kill $(ps aux | grep -E 'flask' | grep -v grep | awk '{print $2}')

## Create user and auth does not have to get pass through the gateway
**testing create user**
curl -d '{"username":"follower1", "email":"follower1@gmail.com", "password":"world123"}' -H "Content-Type: application/json" -X POST http://127.0.0.1:5000/user/create
output: {"email":"follower1@gmail.com","password":"pbkdf2:sha256:150000$IpniaJgR$fcabdd8415da9b2dd96e11c764d8eb9bbfc530c0f77e3fd634690132c4619935","username":"follower1"}

curl -d '{"username":"follower2", "email":"follower2@gmail.com", "password":"world123"}' -H "Content-Type: application/json" -X POST http://localhost:5000/user/create
output: {"email":"follower2@gmail.com","password":"pbkdf2:sha256:150000$3mc92QF8$11978630b2143e9cadc069518a75bc55b95fe917dc7c4800a06159880715883d","username":"follower2"}

**testing auth**
curl -u follower1:world123 -d '{"username":"follower1", "email":"follower1@gmail.com", "password":"world123"}' -H "Content-Type: application/json" -X POST http://127.0.0.1:5000/user/auth

curl -d '{"username":"follower1", "email":"follower1@gmail.com", "password":"world123"}' -H "Content-Type: application/json" -X POST http://127.0.0.1:5000/user/auth

## If its not authorized then the program will output a 401 unAuthorization Error like this
**testing follow user**
curl -d '{"username":"follower1", "user_followed":"follower2"}' -H "Content-Type: application/json" -X POST http://localhost:5000/user/follow
output: ERROR HTTP 401: Authorization headers are missing or are not in Basic format.

curl -u follower1:world123 -d '{"username":"follower1", "user_followed":"follower2"}' -H "Content-Type: application/json" -X POST http://localhost:5000/user/follow
output: {"follower":5,"following":6}
**testing unfollow user**
### Without Auth
curl -d '{"username":"follower1", "user_followed":"follower2"}' -H "Content-Type: application/json" -X POST http://localhost:5000/user/unfollow
output: ERROR HTTP 401: Authorization headers are missing or are not in Basic format.

### With Auth
curl -u follower1:world123 -d '{"username":"follower1", "user_followed":"follower2"}' -H "Content-Type: application/json" -X POST http://localhost:5000/user/unfollow
output: {"follower":5,"following":6}

curl -u follower1:world123 -d '{"username":"follower1", "user_followed":"follower2"}' -H "Content-Type: application/json" -X POST http://localhost:5000/user/follow

**testing tweet**
curl -u follower1:world123 -d '{"username":"follower1", "desc":"Hello World!"}' -H "Content-Type: application/json" -X POST http://localhost:5000/timeline/tweet
output: {"desc":"Hello World!","time":"Thu, 24 Dec 2020 14:25:37 GMT","user":5}

curl -u follower2:world123 -d '{"username":"follower2", "desc":"Hello Follower1!"}' -H "Content-Type: application/json" -X POST http://localhost:5000/timeline/tweet
output: {"desc":"Hello Follower1!","time":"Thu, 24 Dec 2020 14:25:46 GMT","user":6}

**testing home tweet**
curl -u follower1:world123 -d '{"username":"follower1"}' -H "Content-Type: application/json" -X GET http://localhost:5000/timeline/home

**testing public tweet**
curl -u follower1:world123 -d '{"username":"follower1"}' -H "Content-Type: application/json" -X GET http://localhost:5000/timeline/public














**User Services**
**Test createUser:**
curl -d '{"username":"follower1", "email":"follower1@gmail.com", "password":"world123"}' -H "Content-Type: application/json" -X POST http://127.0.0.1:5100/user 


curl -d '{"username":"follower1", "email":"follower1@gmail.com", "password":"world123"}' -H "Content-Type: application/json" -X POST http://127.0.0.1:5000/user/create

curl -d '{"username":"follower2", "email":"follower2@gmail.com", "password":"world123"}' -H "Content-Type: application/json" -X POST http://localhost:5000/user/create


**Output:** {"email":"follower1@gmail.com","password":"pbkdf2:sha256:150000$z4E0juOd$4e6edc229ab741b95d1ad487f4a66ba549b1f87a77fb93eb2cfe568f8a0c9559","username":"follower1"}

curl -d '{"username":"follower2", "email":"follower2@gmail.com", "password":"world123"}' -H "Content-Type: application/json" -X POST http://localhost:5100/user 

**Output:** 
{"email":"follower2@gmail.com","password":"pbkdf2:sha256:150000$UvbCKBQ1$1ffd1a706311e93694a71fa07053e7a2fd1b482bf0f8d9979d18660a786d2059","username":"follower2"}

curl -d '{"username":"follower3", "email":"follower3@gmail.com", "password":"world123"}' -H "Content-Type: application/json" -X POST http://127.0.0.1:5100/user

**Output:**
{"email":"follower3@gmail.com","password":"pbkdf2:sha256:150000$33rKoL2D$35461a464f96a37eddcc4423a4d0465e577da935f642bef2505477ffa404e864","username":"follower3"}

curl -d '{"username":"follower4", "email":"follower4@gmail.com", "password":"world123"}' -H "Content-Type: application/json" -X POST http://127.0.0.1:5100/user

**Output:**
{"email":"follower4@gmail.com","password":"pbkdf2:sha256:150000$RvE54Tmz$a7cb0ba19970df61e8d721707dff0401cd91e84ad7d504d007eced106c42c91e","username":"follower4"}

**Test authorize:**
curl -d '{"username":"follower1", "password":"world123"}' -H "Content-Type: application/json" -X GET http://localhost:5100/user/auth 

curl -d '{"username":"follower1", "password":"world123"}' -H "Content-Type: application/json" -X GET http://localhost:5100/user/auth
**Output:**  
[{"password":"pbkdf2:sha256:150000$9Pnxfbzd$96d3ec6a7deeea595ab8c04ec86a1a0c81df2b9a029d07c9500329fd49f2584e"}]

**Test addFollower:**
//curl -d '{"username":"follower1", "user_followed":"follower2"}' -H "Content-Type: application/json" -X POST http://localhost:5100/follow 
// correct
curl -d '{"username":"follower1", "user_followed":"follower2"}' -H "Content-Type: application/json" -X POST http://localhost:5000/user/follow

**Output:**  
User 5 is now following User 6.

**Test removeFollower:**
curl -d '{"username":"follower1", "user_followed":"follower2"}' -H "Content-Type: application/json" -X POST http://localhost:5100/unfollow

**Output:**  
User 5 has unfollowed User 6.

**Timeline Services **

**Test postTweets:**
curl -d '{"username":"follower1", "desc":"Hello World!"}' -H "Content-Type: application/json" -X POST http://localhost:5200/tweet 
 
**Output:** 
New post on 2020-10-08 21:25:05.009080

curl -d '{"username":"follower2", "desc":"123321foo"}' -H "Content-Type: application/json" -X POST http://localhost:5200/tweet

**Output:**  
New post on 2020-10-08 21:25:45.706694

curl -d '{"username":"follower3", "desc":"hey bro"}' -H "Content-Type: application/json" -X POST http://localhost:5200/tweet

**Output:** 
New post on 2020-10-08 21:31:24.725983

curl -d '{"username":"follower4", "desc":"][][]"}' -H "Content-Type: application/json" -X POST http://localhost:5200/tweet 

**Output:**  
New post on 2020-10-08 21:34:24.924378

**Test getUserTimeline:**
curl -d '{"username":"follower"}' -H "Content-Type: application/json" -X GET http://localhost:5200/user/timeline

**Output:** 
[{"description":"Hello World!","id":1,"time_stamp":"2020-10-09 04:25:05","user_id":5},{"description":"Yea bro","id":6,"time_stamp":"2020-10-09 04:46:12","user_id":5}]


**Test getHomeTimeline:**
curl -d '{"username":"follower1"}' -H "Content-Type: application/json" -X GET http://localhost:5200/home

**Output:** 
[{"description":"123321foo","id":2,"time_stamp":"2020-10-09 04:25:45","user_id":6}]

**Test getPublicTimeline:**
curl -d '{"username":"follower1"}' -H "Content-Type: application/json" -X GET http://localhost:5200/public

**Output:** 
[{"description":"Hello World!","id":1,"time_stamp":"2020-10-09 04:25:05","user_id":5},{"description":"123321foo","id":2,"time_stamp":"2020-10-09 04:25:45","user_id":6},{"description":"hey bro","id":3,"time_stamp":"2020-10-09 04:31:24","user_id":7},{"description":"][][]","id":4,"time_stamp":"2020-10-09 04:34:02","user_id":8},{"description":"][][]","id":5,"time_stamp":"2020-10-09 04:34:24","user_id":8},{"description":"Yea bro","id":6,"time_stamp":"2020-10-09 04:46:12","user_id":5}]

Explanation

We used the following commands: curl, -d, -H, -X, GET, POST

Curl is a tool to transfer data from or to a server, using supported protocols.
-d is used to send specific data in a POST request.
-H stands for headers to supply with request
-X stands for the request method to use
 
**User Services**

Under “Test createUser:” we used curl to transfer data by using -d. The values are correlated with the variables username, email, and password. The variable username takes the value “follower”, variable email takes the value “follower@gmail.com”, and variable password takes the value “world123”. We then used -H to supply with a request for the “Content-Type: application/json” and then used -X to request the method POST to http://localhost:5100/user.
The command is called again but instead of “follower” and “follwer@gmail.com” as the values inputted, the variables email and username use “following” and “following@gmail.com”. Then the command is sent to the same server.

Under “Test aurize:”, curl is used to transfer data with -d. The data is ‘{“username”:”following”,”password”:”world123”}’. -H is then used to supply a request for the Content-Type of application/json with -X to thorequest using the method GET to http://localhost:5100/user/auth.

Under “Test addFollower”, curl is used to transfer data with -d. The data is ‘{“username”:”follower”,”user_followed”:”following””}. With -H, we request for the content type of application/json with -X to POST to http://localhost:5100/follow

Under “Test removeFollower”, curl is used to transfer data with -d. The data is ‘{“username”:”follower”,”user_followed”:”following””}. With -H, we request for the content type of application/json with -X to POST to http://localhost:5100/unfollow

**Timeline Services**

Under “Test postTweets”, curl is used to transfer data with -d. The data is '{"username":"follower", "desc":"Hello World!"}'. With -H, we request for application/json and then used -X to POST to http://localhost:5200/tweet. The other 3 curl commands are to test with the values with the variable username with either “follower” or “following”.

Under “Test getUserTimeline”, curl is used to transfer data with -d. The data is ‘{“username”:”follower”}. With -H, we request for the content type of application/json with -X to GET to http://localhost:5200/user/timeline

Under “Test getHomeTimeline”, curl is used to transfer data with -d. The data is ‘{“username”:”follower”}. With -H, we request for the content type of application/json with -X to POST to http://localhost:5200/home

Under “Test getPublicTimeline”, curl is used to transfer data with -d. The data is ‘{“username”:”follower”}. With -H, we request for the content type of application/json with -X to POST to http://localhost:5200/public


## 5 Password Hashing

In our database in order to keep our users secured we hash our users passwords before storing them into the database. We used werkzeug security helper function “generate_password_hash” to hash our users password when the user is created. Our user is created in “http://localhost:5000/createUser” this is where we store the users username and hash password to the database. Then they will need to use “http://localhost:5000/authenicateUser”, when a user wants to be loged in. They will need to provide their username and password. So when user want to log in they need to be authenticated before logging. This where we will validate the user existence. This api will get the username and hash password from the database and check the users input password matches the hash password. We do this by using werkzeug security helper function “check_password_hash” this will tell us if the user provided us a correct password.
