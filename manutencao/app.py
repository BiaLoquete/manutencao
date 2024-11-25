
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_cors import CORS


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
CORS(app, resources={r"/*": {"origins": "*"}})

from view import *

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
