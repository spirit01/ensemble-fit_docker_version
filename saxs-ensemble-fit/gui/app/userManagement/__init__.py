from flask import Blueprint

userMngmt = Blueprint('userManagement', __name__)

from app.userManagement import views