# CPSC449 - Project2
# Authors: 
Mauricio Macias (mauricio.macias@csu.fullerton.edu) 890741622 <br/>
Ariosto Kuit 	(Ariostokuitak@csu.fullerton.edu) 889834065 <br/>
Andrew Dinh	(decayingapple@csu.fullerton.edu) 893242255 <br/>


### 0 Installation
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

User Services
Test createUser:
 curl -d '{"username":"follower1", "email":"follower1@gmail.com", "password":"world123"}' -H "Content-Type: application/json" -X POST http://127.0.0.1:5000/user 

**Output:** {"email":"follower1@gmail.com","password":"pbkdf2:sha256:150000$z4E0juOd$4e6edc229ab741b95d1ad487f4a66ba549b1f87a77fb93eb2cfe568f8a0c9559","username":"follower1"}


curl -d '{"username":"following", "email":"following@gmail.com", "password":"world123"}' -H "Content-Type: application/json" -X POST http://localhost:5000/user 

Test authorize:
 curl -d '{"username":"follower1", "password":"world123"}' -H "Content-Type: application/json" -X GET http://localhost:5000/user/auth 

**Output:**  
[{"password":"pbkdf2:sha256:150000$z4E0juOd$4e6edc229ab741b95d1ad487f4a66ba549b1f87a77fb93eb2cfe568f8a0c9559"}]

Test addFollower:
 curl -d '{"username":"follower1", "user_followed":"following"}' -H "Content-Type: application/json" -X POST http://localhost:5000/follow 

**Output:**  
User 7 is now following User 6.


Test removeFollower: curl -d '{"username":"follower1", "user_followed":"following"}' -H "Content-Type: application/json" -X POST http://localhost:5000/unfollow

**Output:**  
User 7 has unfollowed User 6.

**Timeline Services **

Test postTweets:
 curl -d '{"username":"follower", "desc":"Hello World!"}' -H "Content-Type: application/json" -X POST http://localhost:5000/tweet 

**Output:** 
New post on 2020-10-07 14:55:04.927286

curl -d '{"username":"follower", "desc":"123321foo"}' -H "Content-Type: application/json" -X POST http://localhost:5000/tweet

**Output:**  
New post on 2020-10-07 14:56:25.477762

curl -d '{"username":"following", "desc":"aifjoasjfoja"}' -H "Content-Type: application/json" -X POST http://localhost:5000/tweet

**Output:** 
New post on 2020-10-07 15:06:17.312504

 curl -d '{"username":"following", "desc":"][][]"}' -H "Content-Type: application/json" -X POST http://localhost:5000/tweet 

**Output:**  
New post on 2020-10-07 15:05:15.194121

Test getUserTImeline: 
curl -d '{"username":"follower"}' -H "Content-Type: application/json" -X GET http://localhost:5000/user/timeline

**Output:** 
[{"description":"Hello World!","id":1,"time_stamp":"2020-10-07 04:06:16","user_id":5},{"description":"Hello World!","id":2,"time_stamp":"2020-10-07 04:18:41","user_id":5},{"description":"Hello World!","id":3,"time_stamp":"2020-10-07 04:21:33","user_id":5},{"description":"Hello World!","id":4,"time_stamp":"2020-10-07 04:26:30","user_id":5},{"description":"Hello World!","id":6,"time_stamp":"2020-10-07 21:55:04","user_id":5},{"description":"123321foo","id":7,"time_stamp":"2020-10-07 21:56:25","user_id":5}]


Test getHomeTimeline:
curl -d ‘{“username”:”follower”}’ -H “Content-Type: application/json" -X GET http://localhost:5000/home

**Output:** 
[{"description":"aifjoasjfoja","id":5,"time_stamp":"2020-10-07 05:59:29","user_id":6},{"description":"][][]","id":8,"time_stamp":"2020-10-07 22:05:15","user_id":6},{"description":"aifjoasjfoja","id":9,"time_stamp":"2020-10-07 22:06:17","user_id":6}]


Test getUserTimeline:
curl -d ‘{“username”:”follower”}’ -H “Content-Type: application/json" -X GET http://localhost:5000/user/timeline

**Output:**  
[{"description":"Hello World!","id":1,"time_stamp":"2020-10-07 04:06:16","user_id":5},{"description":"Hello World!","id":2,"time_stamp":"2020-10-07 04:18:41","user_id":5},{"description":"Hello World!","id":3,"time_stamp":"2020-10-07 04:21:33","user_id":5},{"description":"Hello World!","id":4,"time_stamp":"2020-10-07 04:26:30","user_id":5},{"description":"Hello World!","id":6,"time_stamp":"2020-10-07 21:55:04","user_id":5},{"description":"123321foo","id":7,"time_stamp":"2020-10-07 21:56:25","user_id":5}]

Test getPublicTimeline:
curl -d '{"username":"follower"}' -H "Content-Type: application/json" -X GET http://localhost:5000/public

**Output:** 
[{"description":"Hello World!","id":1,"time_stamp":"2020-10-07 04:06:16","user_id":5},{"description":"Hello World!","id":2,"time_stamp":"2020-10-07 04:18:41","user_id":5},{"description":"Hello World!","id":3,"time_stamp":"2020-10-07 04:21:33","user_id":5},{"description":"Hello World!","id":4,"time_stamp":"2020-10-07 04:26:30","user_id":5},{"description":"aifjoasjfoja","id":5,"time_stamp":"2020-10-07 05:59:29","user_id":6},{"description":"Hello World!","id":6,"time_stamp":"2020-10-07 21:55:04","user_id":5},{"description":"123321foo","id":7,"time_stamp":"2020-10-07 21:56:25","user_id":5},{"description":"][][]","id":8,"time_stamp":"2020-10-07 22:05:15","user_id":6},{"description":"aifjoasjfoja","id":9,"time_stamp":"2020-10-07 22:06:17","user_id":6}]

Explanation

We used the following commands: curl, -d, -H, -X, GET, POST

Curl is a tool to transfer data from or to a server, using supported protocols.
-d is used to send specific data in a POST request.
-H stands for headers to supply with request
-X stands for the request method to use
 
**User Services**

Under “Test createUser:” we used curl to transfer data by using -d. The values are correlated with the variables username, email, and password. The variable username takes the value “follower”, variable email takes the value “follower@gmail.com”, and variable password takes the value “world123”. We then used -H to supply with a request for the “Content-Type: application/json” and then used -X to request the method POST to http://localhost :5000/user.
The command is called again but instead of “follower” and “follwer@gmail.com” as the values inputted, the variables email and username use “following” and “following@gmail.com”. Then the command is sent to the same server.

Under “Test aurize:”, curl is used to transfer data with -d. The data is ‘{“username”:”following”,”password”:”world123”}’. -H is then used to supply a request for the Content-Type of application/json with -X to thorequest using the method GET to http://localhost:5000/user/auth.

Under “Test addFollower”, curl is used to transfer data with -d. The data is ‘{“username”:”follower”,”user_followed”:”following””}. With -H, we request for the content type of application/json with -X to POST to http://localhost:5000/follow

Under “Test removeFollower”, curl is used to transfer data with -d. The data is ‘{“username”:”follower”,”user_followed”:”following””}. With -H, we request for the content type of application/json with -X to POST to http://localhost:5000/unfollow

**Timeline Services**

Under “Test postTweets”, curl is used to transfer data with -d. The data is '{"username":"follower", "desc":"Hello World!"}'. With -H, we request for application/json and then used -X to POST to http://localhost:5000/tweet. The other 3 curl commands are to test with the values with the variable username with either “follower” or “following”.

Under “Test getUserTimeline”, curl is used to transfer data with -d. The data is ‘{“username”:”follower”}. With -H, we request for the content type of application/json with -X to GET to http://localhost:5000/user/timeline

Under “Test getHomeTimeline”, curl is used to transfer data with -d. The data is ‘{“username”:”follower”}. With -H, we request for the content type of application/json with -X to POST to http://localhost:5000/home

Under “Test getPublicTimeline”, curl is used to transfer data with -d. The data is ‘{“username”:”follower”}. With -H, we request for the content type of application/json with -X to POST to http://localhost:5000/public




## 5 Password Hashing

In our database in order to keep our users secured we hash our users passwords before storing them into the database. We used werkzeug security helper function “generate_password_hash” to hash our users password when the user is created. Our user is created in “http://localhost:5000/createUser” this is where we store the users username and hash password to the database. Then they will need to use “http://localhost:5000/authenicateUser”, when a user wants to be loged in. They will need to provide their username and password. So when user want to log in they need to be authenticated before logging. This where we will validate the user existence. This api will get the username and hash password from the database and check the users input password matches the hash password. We do this by using werkzeug security helper function “check_password_hash” this will tell us if the user provided us a correct password.
