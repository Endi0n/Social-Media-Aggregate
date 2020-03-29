from .test import *
from .linkedin import linkedin
from .twitter import twitter
from .tumblr import tumblr
from .auth import auth
from app import app

app.register_blueprint(linkedin)
app.register_blueprint(twitter)
app.register_blueprint(tumblr)
app.register_blueprint(auth)
