#!/var/www/bakalarka/flask/bin/python

import os
from wsgiref.handlers import CGIHandler
from app import create_app, admin, models, db
from flask.ext.admin.menu import MenuLink

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

admin.add_view(models.UserView(models.User, db.session))
admin.add_link(MenuLink(name='Back', category='', url="/home"))


CGIHandler().run(app)

