from .test import *
from .errors import *
from .platforms import *
from .common import *
from .auth import auth
from app import app

app.register_blueprint(auth)
