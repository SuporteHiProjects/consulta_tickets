from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FileField
from wtforms.validators import DataRequired, Email
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_wtf.csrf import CSRFProtect
import base64
import os
import requests
import datetime
import time
import pytz
import json
import app_data as function
from forms import TicketForm

app = Flask(__name__, static_url_path='/static')

url_inbox = "https://api.directtalk.com.br/1.5/ticket/"
busca_ticket_email = "tickets?desc=true"
ticket_detail = "tickets/"
Authorization = "Basic ZHRzMTg2ZTIzYWNkLTBiZDYtNGE4YS1iNTFlLWNiOGIzMWExZmI2ZTpkdnZic2tobTZhdHd0OWVscGNzdg=="

# Página de login
@app.route('/')
def index():
    return render_template('login.html')

# Página de consulta de tickets
@app.route('/consulta_ticket', methods=['GET', 'POST'])
def consulta_ticket():
    if request.method == 'POST':
        data = request.form
        login = data['login']
        email = data['email']
        senha = data['senha']
        credentials = f"{login}:{senha}"
        credentials_base64 = base64.b64encode(credentials.encode()).decode()
        headers = {
            'Authorization': f'Basic {credentials_base64}'
        }
        url = "https://tenant.directtalk.com.br/1.0/tenants?filter=dts1"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
          headers1 = {
                'Authorization': Authorization
            }
          url1 = url_inbox + busca_ticket_email + "&externaldata=email|" + email
          response1 = requests.get(url1, headers=headers1)
          tickets = response1.json()
          tickets = function.rounded_dates(tickets)
          tickets = function.slice_tickets(tickets)
          return render_template('tickets.html', tickets=tickets)
        else:
            return render_template('login.html', message="Login inválido. Tente novamente.")
    return render_template('login.html')

# Página de detalhes do ticket
@app.route('/ticket/<string:ticket_id>', methods=['GET'])
def ticket_details(ticket_id):
    headers = {
        'Authorization': Authorization
    }
    url = f"https://api.directtalk.com.br/1.5/ticket/tickets/{ticket_id}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
      ticket_details = response.json()
      description_html = ticket_details.get('description', '')
      ticket_details['description'] = description_html
      timestamp = ticket_details['deadline']
      if timestamp != None:
        deadline_utc = datetime.datetime.utcfromtimestamp(timestamp)
        utc_timezone = pytz.timezone('UTC')
        deadline_utc = utc_timezone.localize(deadline_utc)
        brasil_timezone = pytz.timezone('America/Sao_Paulo')
        deadline_brasil = deadline_utc.astimezone(brasil_timezone)
        format_deadline_utc = deadline_brasil.strftime('%d/%m/%Y %H:%M')
        ticket_details['deadline'] = format_deadline_utc
      else:
        ticket_details['deadline'] = "Sem registro"
      comments_url = f"https://api.directtalk.com.br/1.5/ticket/tickets/{ticket_id}/comments/public"
      comments_response = requests.get(comments_url, headers=headers)
      if comments_response.status_code == 200:
        comments = comments_response.json()
      else:
        comments = []
      return render_template('ticket_details.html', ticket_details=ticket_details, comments=comments)
    else:
      return "Erro ao buscar detalhes do ticket."


#Responder ticket
@app.route('/responder_ticket/<string:ticket_id>', methods=['POST', 'GET'])
def responder_ticket(ticket_id):
    if request.method == 'POST':
        content = request.form['resposta']

        # Requisição
        comment_data = {
            "id": ticket_id,
            "content": content,
            "DefaultCreatorId": "d4386622-e980-48a5-9170-870d4e81c58e"
        }

        # URL para adicionar um comentário ao ticket
        add_comment_url = f"https://agent.directtalk.com.br/1.0/ticket/consumer/{ticket_id}/addcomment"

        # Realizar POST
        headers = {
            'Content-Type': 'application/json',
            'Authorization': Authorization,
        }

        try:
            response = requests.post(add_comment_url, data=json.dumps(comment_data), headers=headers)

            if response.status_code == 200:
                return redirect(url_for('ticket_details', ticket_id=ticket_id))
            else:
                return "Erro ao responder ao ticket."
        except Exception as e:
            return f"Erro ao responder ao ticket: {str(e)}"

    else:
        return render_template('responder_ticket.html', ticket_id=ticket_id)
      

# adicionar comentário
@app.route('/adicionar_anexos/<string:ticket_id>', methods=['POST', 'GET'])
def adicionar_anexos(ticket_id):
    if request.method == 'POST':

        if 'anexos[]' not in request.files:
            return "Nenhum arquivo anexado."

        anexos = request.files.getlist('anexos[]')

        if not anexos:
            return "Nenhum arquivo anexado."
        userid = "d4386622-e980-48a5-9170-870d4e81c58e"  # ID do módulo
        publicAttach = True  # Define se os anexos são públicos ou privados.

        try:
            for anexo in anexos:

                add_attachment_url = f"https://api.directtalk.com.br/1.5/ticket/tickets/{ticket_id}/attachments?userid={userid}&publicAttach={publicAttach}"


                headers = {
                    'Content-Type': 'multipart/form-data',
                    'Authorization': Authorization
                }

                files = {'file': (anexo.filename, anexo.stream.read())}
                response = requests.post(add_attachment_url, files=files, headers=headers)

                if response.status_code != 201:
                    return "Erro ao adicionar anexo ao ticket."


            return redirect(url_for('ticket_details', ticket_id=ticket_id))
        except Exception as e:
            return f"Erro ao adicionar anexos ao ticket: {str(e)}"

    else:
        return render_template('adicionar_anexos.html', ticket_id=ticket_id)



# criar ticket
@app.route('/criar_ticket', methods=['POST', 'GET'])
def criar_ticket():
    form = TicketForm()
    if request.method == 'POST' and form.validate_on_submit():
        # Acessar os dados do formulário
        nome = form.nome.data
        email = form.email.data
        cc = form.cc.data
        assunto = form.assunto.data
        prioridade = form.prioridade.data
        descricao = form.descricao.data
        anexo = form.anexo.data

    return render_template('criar_ticket.html', form=form)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
