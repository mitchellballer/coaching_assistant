Coaching assistant is going to be a tool that help coaches better see their athletes information in one place.

Coaches will be able to invite athletes to their 'group' or 'team'. After authentication and permissions
are accepted, the coach will be able to see a summary of that athletes training on a dashboard. Ideally
a calendar with weekly milage, recent workout highlights, comments etc.

export FLASK_APP=__init__.py

source venv/bin/activate

Rebuilding the database:
    -Stop current instance
    export FLAS_APP=flaskr
    export FLASK_ENV=development
    -flask init-db
        calls db.py > init_db()
    -flask run

testing the application:
With server running, in root directory:
$ pytest
    
prerequisites:
-python module 'request'
-config.properties in same directory with:
    [TOKEN]
    bearer_token = 
    bearer_token_expiration = 0
    refresh_token = 

    [CLIENT]
    client_id = [your client id]
    client_secret = [your client secret]

    [ATHLETE]
    my_athlete_id = [your athlete id]