from flask import Flask

app = Flask(__name__)

from . import routes  # Import routes to register them with the app