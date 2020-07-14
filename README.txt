Coaching assistant is going to be a tool that help coaches better see their athletes information in one place.

Coaches will be able to invite athletes to their 'group' or 'team'. After authentication and permissions
are accepted, the coach will be able to see a summary of that athletes training on a dashboard. Ideally
a calendar with weekly milage, recent workout highlights, comments etc.

prerequisites:
-python module 'request'
-config.properties in same directory with:
    [TOKEN]
    bearer_token = 
    bearer_token_expiration = 0

    [CLIENT]
    client_id = [your client id]
    client_secret = [your client secret]

    [ATHLETE]
    my_athlete_id = [your athlete id]