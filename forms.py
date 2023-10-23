from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FileField, validators
from wtforms.validators import DataRequired, Email

class TicketForm(FlaskForm):
  email = StringField('E-mail', validators=[DataRequired(), Email()])
  copyaddress = StringField('CC', validators=[validators.Optional()])
  ticketTitle = StringField('Assunto', validators=[DataRequired()])
  ticketContent = TextAreaField('Descrição', validators=[DataRequired()])
  file = FileField('Anexo')