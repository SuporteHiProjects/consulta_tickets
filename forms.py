from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FileField
from wtforms.validators import DataRequired, Email

class TicketForm(FlaskForm):
    # Cabeçalho
    nome = StringField('Nome', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    cc = StringField('CC')

    # Conteúdo
    assunto = StringField('Assunto', validators=[DataRequired()])
    prioridade = SelectField('Prioridade', choices=[('baixa', 'Baixa'), ('normal', 'Normal'), ('alta', 'Alta'), ('urgente', 'Urgente')])
    descricao = TextAreaField('Descrição', validators=[DataRequired()])
    anexo = FileField('Anexo')
    
    # Botão
    submit = StringField('Enviar') 