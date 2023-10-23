from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FileField
from wtforms.validators import DataRequired, Email
from flask import Flask, make_response, request, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
import base64
import os
import requests
import datetime
import time
import json
import app_data as function
from forms import TicketForm

app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = '12345'

url_inbox = "https://api.directtalk.com.br/1.5/ticket/"
busca_ticket_email = "tickets?desc=true"
ticket_detail = "tickets/"
Authorization = os.environ['Authorization Inbox']

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/favicon.ico')
def no_favicon():
    return make_response("", 204)

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
      createDate = ticket_details['creationDate']
      fixSLA = function.fixTimezone(timestamp)
      fixCreateDate = function.fixTimezone(createDate)
      ticket_details['deadline'] = fixSLA
      ticket_details['creationDate'] = fixCreateDate
      comments_url = f"https://api.directtalk.com.br/1.5/ticket/tickets/{ticket_id}/comments/public"
      comments_response = requests.get(comments_url, headers=headers)
      if comments_response.status_code == 200:
        comments = comments_response.json()
        comments.reverse()
        for i in range(len(comments)):
          fixData = function.fixTimezone(comments[i]['date'])
          comments[i]['date'] = fixData
      else:
        comments = []
      fenixToken = function.generateFenixToken()
      ticketId = ticket_details['id']
      emailsData = function.getEmailsTransitData(fenixToken, ticketId)
      return render_template('ticket_details.html', ticket_details=ticket_details, comments=comments, fenixToken=fenixToken, emailsData=emailsData)
    else:
      return "Erro ao buscar detalhes do ticket."

@app.route('/responder_ticket/<string:ticket_id>', methods=['POST', 'GET'])
def responder_ticket(ticket_id):
    if request.method == 'POST':
        content = request.form['resposta']
        comment_data = {
            "id": ticket_id,
            "content": content,
            "DefaultCreatorId": "d4386622-e980-48a5-9170-870d4e81c58e"
        }
        add_comment_url = f"https://agent.directtalk.com.br/1.0/ticket/consumer/{ticket_id}/addcomment"
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
    if request.method == 'POST':
      address = form.email.data
      copyaddress = form.copyaddress.data
      ticketTitle = form.ticketTitle.data
      ticketContent = form.ticketContent.data
      access_file = request.files['file']
      print(access_file)
    return render_template('criar_ticket.html', form=form)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
