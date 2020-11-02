database_init: FLASK_APP=project/user_api/app.py flask init && FLASK_APP=project/timeline_api/app.py flask init
gateway: FLASK_APP=gateway/gateway.py flask run -p $PORT
users: FLASK_APP=project/user_api/app.py flask run -p $PORT
timelines: FLASK_APP=project/timeline_api/app.py flask run -p $PORT
