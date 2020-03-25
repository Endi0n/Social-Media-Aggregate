from .test import *
from .linkedin import linkedin
from app import app

app.register_blueprint(linkedin)
