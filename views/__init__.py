from .test import *
from .linkedin import linkedin
from .twitter import twitter
from app import app

app.register_blueprint(linkedin)
app.register_blueprint(twitter)
