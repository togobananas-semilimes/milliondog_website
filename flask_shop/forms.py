from flask.ext.wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired

class LoginForm(Form):
    name = StringField('name', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)

class CheckoutForm(Form):
    name = StringField('name', validators=[DataRequired()])
    name2 = StringField('name2')
    street = StringField('street', validators=[DataRequired()])
    street2 = StringField('street2')
    zip = StringField('zip', validators=[DataRequired()])
    city = StringField('city', validators=[DataRequired()])
    state = StringField('state')
    country = StringField('country', validators=[DataRequired()])
    delivery = BooleanField('delivery', default=False)
    invoice = BooleanField('invoice', default=False)

class ContactForm(Form):
    name = StringField('name', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])
    message = StringField('message', validators=[DataRequired()])
    answer = StringField('answer', validators=[DataRequired()])