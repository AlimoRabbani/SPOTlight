__author__ = 'Alimohammad'

from flask import Flask, render_template
from flask_login import LoginManager
import json

from views.common_views import common_views
from views.user_views import user_views
from views.admin_views import admin_views
from data_model import User

class ReverseProxied(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        scheme = environ.get('X-Forwarded-Proto', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)


app = Flask(__name__)
app.wsgi_app = ReverseProxied(app.wsgi_app)
app.register_blueprint(common_views)
app.register_blueprint(user_views)
app.register_blueprint(admin_views)
app.config["custom_config"] = json.loads(open("config.json").read())

app.secret_key = app.config["custom_config"]["secret_key"]

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "common_views.index"


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

@app.errorhandler(404)
def forbidden(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
