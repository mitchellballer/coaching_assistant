import os

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    #import our database
    from . import db
    #initialize our database
    db.init_app(app)

    #import and register our authentication blueprint
    from . import auth
    app.register_blueprint(auth.bp)

 #   #import and register our calendar blueprint
    from . import calendar
    app.register_blueprint(calendar.bp)
    app.add_url_rule('/', endpoint='index')

    #import and register our activity blueprint
    from . import activity
    app.register_blueprint(activity.bp)

    return app