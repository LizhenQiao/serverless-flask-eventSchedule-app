from flask import Flask
from flask_bootstrap import Bootstrap
webapp = Flask(__name__)
webapp.secret_key = "you-will-never-know-lol"
webapp.jinja_env.auto_reload = True
webapp.config['TEMPLATES_AUTO_RELOAD'] = True
webapp.config['SESSION_TYPE'] = 'filesystem'
Bootstrap(webapp)
from app import user
from app import main
from app import event
from app import config
