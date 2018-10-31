#!/home/yayo/virtual_enviroment/bin/python
import os
from app import create_app, db, admin, models
from app.models import User, Role
from flask.ext.script import Manager, Shell
from flask.ext.admin.menu import MenuLink


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)

admin.add_view(models.UserView(models.User, db.session))
admin.add_link(MenuLink(name='Back', category='', url="/home"))


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)

manager.add_command("shell", Shell(make_context=make_shell_context))

if __name__ == '__main__':
    manager.run()