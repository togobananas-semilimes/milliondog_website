from flask import Flask, g
from flask.ext.login import LoginManager
from flask.ext.babel import Babel
from flask.json import JSONEncoder


app = Flask(__name__)
app.config.from_object('config')
babel = Babel(app)
lm = LoginManager()
lm.init_app(app)
from flask_shop import views
from flask_shop import server

class CustomJSONEncoder(JSONEncoder):
    """This class adds support for lazy translation texts to Flask's
    JSON encoder. This is necessary when flashing translated texts."""
    def default(self, obj):
        from speaklater import is_lazy_string
        if is_lazy_string(obj):
            try:
                return unicode(obj)  # python 2
            except NameError:
                return str(obj)  # python 3
        return super(CustomJSONEncoder, self).default(obj)

app.json_encoder = CustomJSONEncoder