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
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import werkzeug.utils
import hashlib
from werkzeug.datastructures import FileStorage
import subprocess
import os
import logging
from io import BytesIO


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
        plataforma = data['product']
        login = data['login']
        email = data['email']
        senha = data['senha']
        empresa_codigo = data['empresa_codigo']
        plataforma_social = None

        if plataforma == "Supervisor":
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

        elif plataforma == "HiFlow":
            empresa_codigo = data.get('empresa_codigo')
            if not empresa_codigo:
                return render_template('login.html', message="Código da empresa é obrigatório para o Flow")

            senha_md5 = hashlib.md5(senha.encode()).hexdigest()

            flow_login_url = 'http://app.akna.com.br/emkt/int/integracao.php'
            flow_data = {
                'User': email,
                'Pass': senha_md5,
                'Client': empresa_codigo
            }
            flow_response = requests.post(flow_login_url, data=flow_data)
            if flow_response.status_code == 200:
                headers1 = {
                    'Authorization': Authorization
                }
                url1 = url_inbox + busca_ticket_email + "&externaldata=email|" + email
                response1 = requests.get(url1, headers=headers1)
                tickets = response1.json()
                tickets = function.rounded_dates(tickets)
                tickets = function.slice_tickets(tickets)
                return render_template('tickets.html', tickets=tickets)
            elif flow_response.status_code == 401:
                return render_template('login.html', message="Dados de acesso inválido, verifique suas credenciais e se você é um administrador Hi Flow")

        elif plataforma == "Yourviews":
            yourviews_login_url = 'https://service.yourviews.com.br/admin/account/login?returnUrl=%2Fadmin%2FDashboard'
            yourviews_headers = {
                'Accept': 'application/xml',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            yourviews_data = {
                'username': email,
                'password': senha,
                'RememberMe': 'false'
            }
            yourviews_response = requests.post(yourviews_login_url, headers=yourviews_headers, data=yourviews_data)

            if 'Dados inválidos' in yourviews_response.text:
                return render_template('login.html', message="Dados de login Yourviews inválidos. Tente novamente.")
            elif "Por favor, responda ao captcha abaixo" in yourviews_response.text:
                return render_template('login.html', message="Excesso de tentativas incorretas. <br> Acesse sua plataforma de Yourviews, faça logout, entre com suas credenciais e preencha o captcha solicitado.")
            elif 'Dados inválidos' not in yourviews_response.text:
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


def enviar_anexos(ticket_id):
  userid = "d4386622-e980-48a5-9170-870d4e81c58e"  # ID do módulo
  publicAttach = True  # Define se os anexos são públicos ou privados.
  
  for anexo in request.files.getlist('new_comment_anexos[]'):
      add_attachment_url = f"https://api.directtalk.com.br/1.5/ticket/tickets/{ticket_id}/attachments?userid={userid}&publicAttach={publicAttach}"
  
      headers = {
          'Authorization': Authorization
      }
  
      try:
          file_stream = BytesIO()
          file_stream.write(anexo.read())
          file_stream.seek(0)  # Voltar ao início do fluxo
  
          files = {'file': (anexo.filename, file_stream)}
          response = requests.post(add_attachment_url, files=files, headers=headers)
  
          if response.status_code != 201:
              return "Erro ao adicionar anexo ao ticket na função de enviar anexos."
      except Exception as e:
          return f"Erro ao processar anexo: {str(e)}"
  
  return redirect(url_for('ticket_details', ticket_id=ticket_id))

def send_image_to_directtalk(image, ticket_id):
  url = f'https://api.directtalk.com.br/1.5/ticket/tickets/{ticket_id}/attachments?userid=d4386622-e980-48a5-9170-870d4e81c58e&publicAttach=True'

  headers = {
      'Authorization': Authorization
  }

  files = {
      'image': (image.filename, image.stream)
  }

  response = requests.post(url, headers=headers, files=files)

  app.logger.info(f'Request URL: {url}')
  app.logger.info(f'Response Status Code: {response.status_code}')
  app.logger.info(f'Response Content: {response.text}')

  if response.status_code == 201:
      return {'message': 'Imagem enviada com sucesso'}
  else:
      return {'error': 'Falha ao enviar a imagem'}


# responder ticket
@app.route('/responder_ticket/<string:ticket_id>', methods=['POST', 'GET'])
def responder_ticket(ticket_id):
    if request.method == 'POST':
        content = request.form['new_comment_content']
        anexos = request.files.getlist('new_comment_anexos[]')  # Receba os anexos enviados
        print(content)

        comment_data = json.dumps({
            "id": ticket_id,
            "content": content,
            "DefaultCreatorId": "d4386622-e980-48a5-9170-870d4e81c58e"
        })

        add_comment_url = f"https://agent.directtalk.com.br/1.0/ticket/consumer/{ticket_id}/addcomment"
        headers = {
            'Authorization': Authorization,
            'content-type': 'application/json'
        }

        response = requests.post(add_comment_url, data=comment_data, headers=headers)

        if response.status_code == 200:
            print("ok")
            print("Entrou", anexos)
            file_storage = anexos[0]
            if file_storage.filename.strip() != "":
                return enviar_anexos(ticket_id)
            else:
                return redirect(url_for('ticket_details', ticket_id=ticket_id))
        else:
            print(response.status_code)
            return "Erro ao responder ao ticket."

    else:
        return render_template('responder_ticket.html', ticket_id=ticket_id)

# adicionar anexo
@app.route('/adicionar_anexos/<string:ticket_id>', methods=['POST', 'GET'])
def adicionar_anexos(ticket_id):
    if request.method == 'POST':
        if 'anexos[]' not in request.files:
            return "Nenhum arquivo anexado."

        anexos = request.files.getlist('anexos[]')

        if not anexos:
            return "Nenhum arquivo anexado."

        try:
            return enviar_anexos(ticket_id, anexos)
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
        access_files = request.files.getlist('anexos[]')

        # Configurações de e-mail
        remetente = 'carlos.gomes@hiplatform.com'
        senha = 'bauovhzgdtgllyxu'
        destinatario = 'servicedesk@hiplatform.com'
        reply_to = address
        cc = [copyaddress]
        cco = []

        # Criar o objeto de mensagem
        mensagem = MIMEMultipart()
        mensagem['From'] = remetente
        mensagem['To'] = destinatario
        mensagem['Reply-To'] = reply_to
        mensagem['Subject'] = ticketTitle

        # Adicionar CC
        mensagem['Cc'] = ', '.join(cc)

        # Corpo do e-mail
        corpo = ticketContent
        mensagem.attach(MIMEText(corpo, 'plain'))

        if access_files:
            print("Entrou", access_files)
            file_storage = access_files[0]
            if file_storage.filename.strip() != "":
                for anexo_file in access_files:
                    anexo_arquivo = secure_filename(anexo_file.filename)
                    with open(anexo_arquivo, 'wb') as arquivo:
                        arquivo.write(anexo_file.read())

                    with open(anexo_arquivo, 'rb') as arquivo:
                        anexo = MIMEApplication(arquivo.read(), _subtype="pdf")
                        anexo.add_header('content-disposition', 'attachment', filename=anexo_arquivo)
                        mensagem.attach(anexo)

                    # Excluir o arquivo após o envio
                    os.remove(anexo_arquivo)
        # Conectar ao servidor SMTP
        servidor_smtp = smtplib.SMTP('smtp.gmail.com', 587)
        servidor_smtp.starttls()
        servidor_smtp.login(remetente, senha)

        # Montar a lista de destinatários, incluindo CC e CCO
        destinatarios = [destinatario] + cc + cco

        # Enviar o e-mail
        servidor_smtp.sendmail(remetente, destinatarios, mensagem.as_string())

        # Encerrar a conexão
        servidor_smtp.quit()

        print('E-mail com anexos enviados com sucesso!')

    return render_template('criar_ticket.html', form=form)

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=8080, debug=True)
