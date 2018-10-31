from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, TextAreaField, IntegerField, FloatField, RadioField
from wtforms.fields.html5 import DecimalRangeField
from wtforms.validators import DataRequired, NumberRange, Length
from flask_wtf.file import FileAllowed, FileField


# A form for computation
#
class Computation(Form):
    title = StringField('Title:', validators=[DataRequired("Required a title!"), Length(1, 35)])
    description = TextAreaField('Description:')

#   Currently we only support pdb
#   models = FileField('File with model/models:', validators=[DataRequired("Required a file with model or models. Allowed formats are 'pdb', 'zip', 'tar.gz', 'rar' or 'tar.bz2'"),
#                                                              FileAllowed(['pdb', 'zip', 'tar.gz', 'rar', 'tar.bz2'])])
    models = FileField('File with model/models:', validators=[DataRequired("Required a file with model or models. Required format is 'pdb'"),
                                                              FileAllowed(['pdb'])])
    expData = FileField('File with experiment data:', validators=[DataRequired("Required a text file with experiment data!")])
    qRange = DecimalRangeField('q range:', validators=[DataRequired("Required parameter")], default=0.1)
    calcType = RadioField('Calculation type:', choices=[('random_walk', 'Random walk'), ('stunnel', 'Stochastic tunneling')], default='random_walk')
    calcSteps = IntegerField('Calculation steps:',
                             validators=[DataRequired("Required an integer number!"),
                                         NumberRange(500, 1000000, "Minimum value is 10 000, maximum value is 1000000!")], default=500)
    stepsBetweenSync = IntegerField('Steps between synchronization:',
                                    validators=[NumberRange(100, 10000, "Minimum value is 100, maximum value is 10000!")], default=100)
    alpha = FloatField('alpha - max. random step:', default=0.01)
    beta = FloatField('beta - chi2 acceptance:', default=0.005)
    gamma = FloatField('gamma - tunel scaling:', default=500)
    submit = SubmitField('Submit')


# A register form
#
class RegistrationForm(Form):
    username = StringField('Username:', validators=[DataRequired("Required Field!")])
    email = StringField('Email:', validators=[DataRequired("Required Field!")])
    comment = TextAreaField('Why do you want to sign up?', validators=[DataRequired("Required field!"), Length(20, message="Minimum of 20 characters required!")])
    submit = SubmitField('Sign Up')
