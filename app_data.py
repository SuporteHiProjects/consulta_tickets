import datetime
import time
import json
import time
import pytz
import requests
import os
import base64
import random
import string
import smtplib
from email.mime.text import MIMEText


my_secret = os.environ['Authorization Inbox']

def gen_supdt_basic():
  url = "https://tenant.directtalk.com.br/1.0/user/hijack/dts1supdt"
  payload = "{}"
  headers = {
      'Authorization': my_secret
  }

  try:
      response = requests.get(url, headers=headers, data=payload)
      response.raise_for_status()
      response_content = response.text

      if response_content is not None:
          # Construir a string 'dts1supt:response'
          basic_string = f"dts1supdt:{response_content}"

          # Codificar a string para Base64
          base64_encoded = base64.b64encode(basic_string.encode()).decode()
          new_auth = f"Basic " + base64_encoded
          #print(new_auth)

          # Chamar a função generateFenixToken() e obter o token
          fenix_token = generateFenixToken(new_auth)
          return fenix_token
      else:
          #print("Não foi possível obter o response para gerar o Token Basic.")
          return None
  except requests.exceptions.HTTPError as err:
      #print(f"HTTP Error: {err}")
      return None

def generateFenixToken(new_auth):
  url = "https://www3.directtalk.com.br/adminuiservices/api/Login"
  payload = "{}"
  
  headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': new_auth
  }
  response = requests.post(url, headers=headers, data=payload)
  token_data = response.json()
  token = token_data['token']
  return token



def getEmailsTransitData(fenixToken, ticketId):
  url = "https://app.hiplatform.com/agent/ticket/1.0/ticket/maininfos/" + ticketId
  payload = {}
  headers = {
  'authority': 'app.hiplatform.com',
  'accept': '*/*',
  'accept-language': 'application/json',
  'authorization': 'DT-Fenix-Token ' + fenixToken,
  'content-type': 'application/json'
  }
  response = requests.request("GET", url, headers=headers, data=payload)
  emailsTransitData = response.json()
  return emailsTransitData

def fixTimezone(timestamp):
  if timestamp != None:
      deadline_utc = datetime.datetime.utcfromtimestamp(timestamp)
      utc_timezone = pytz.timezone('UTC')
      deadline_utc = utc_timezone.localize(deadline_utc)
      brasil_timezone = pytz.timezone('America/Sao_Paulo')
      deadline_brasil = deadline_utc.astimezone(brasil_timezone)
      formated_data = deadline_brasil.strftime('%d/%m/%Y %H:%M')
      return formated_data
  else:
    return "Sem registro"

def rounded_dates(ticketsData):
  for i in range(len(ticketsData)):
    reference_data = ticketsData[i]['creationDate']
    date_now = time.time()
    diference_in_seconds_with_dates = date_now - reference_data
    diference_in_days_with_dates = diference_in_seconds_with_dates / (60 * 60 * 24)
    rounded_diference = int(round(diference_in_days_with_dates))
    if rounded_diference == 0:
      ticketsData[i]['createDate_diference_days'] = "Hoje"
    elif rounded_diference == 1:
      ticketsData[i]['createDate_diference_days'] = "Ontem"
    elif rounded_diference >= 2 and rounded_diference <= 30:
      ticketsData[i]['createDate_diference_days'] = "Há " + str(rounded_diference) + " dias"
    elif rounded_diference > 30:
      ticketsData[i]['createDate_diference_days'] = "Há mais de um mês"
  return ticketsData

def slice_tickets(ticketsData):
  splitedTickets = {
    "finalizados": {
      "total": 0,
      "data": []
    },
    "abertos": {
      "total": 0,
      "data": []
    },
    "aguardando_resposta": {
      "total": 0,
      "data": []
    },
  }
  ticketsData.insert(0,splitedTickets)
  for i in range(1,len(ticketsData)):
    if ticketsData[i]['state']['name'] == 'Aberto' or ticketsData[i]['state']['name'] == 'Em andamento' or ticketsData[i]['state']['name'] == 'Reaberto':
      ticketsData[0]['abertos']['data'].append(ticketsData[i])
    elif ticketsData[i]['state']['name'] == 'Aguardando resposta':
      ticketsData[0]['aguardando_resposta']['data'].append(ticketsData[i])
    elif ticketsData[i]['state']['name'] == 'Finalizado':
      ticketsData[0]['finalizados']['data'].append(ticketsData[i])
    else:
      return "Ocorreu um erro"
  ticketsData[0]['abertos']['total'] = len(ticketsData[0]['abertos']['data'])
  ticketsData[0]['aguardando_resposta']['total'] = len(ticketsData[0]['aguardando_resposta']['data'])
  ticketsData[0]['finalizados']['total'] = len(ticketsData[0]['finalizados']['data'])
  return ticketsData

def generate_pin():
  pin = random.randint(10000000, 99999999)
  return str(pin)

def send_email(email):
  # Geração do PIN aleatório
  pin = generate_pin()

  # Configurações de e-mail
  remetente = 'servicedesk@hiplatform.com'
  senha = 'riilmqnupaofwavu'
  destinatario = email
  reply_to = 'no-reply@directtalk.com'

  # Criar o objeto de mensagem
  mensagem_html = f'''<html>
    <body>
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ccc; border-radius: 5px; background-color: #f9f9f9;">
            <img src="https://files.directtalk.com.br/1.0/api/file/public/98318821-47c9-4d53-a6fd-4aefe26c4cf5/content-inline" alt="Logo Hi Platform" width="200" style="display: block; margin: 0 auto;">
            <p style="margin-bottom: 10px;">Caro usuário,</p>
            <p style="margin-bottom: 10px;">Você acabou de receber um código PIN de acesso.</p>
            <p style="margin-bottom: 10px;">O código PIN aleatório é: <strong style="color: #0056b3; display: inline-block; padding: 5px 10px; margin-left: 5px; border-radius: 5px; background-color: #0056b3; color: #fff;">{pin}</strong></p>
            <p style="margin-bottom: 10px;">Para confirmar seu login, por favor, digite o código PIN recebido na plataforma Hi.</p>
            <p>Atenciosamente,</p>
            <p style="margin-top: 20px; color: #666;">Equipe Hi Platform</p>
        </div>
    </body>
</html>'''

  mensagem = MIMEText(mensagem_html, 'html')

  mensagem['From'] = remetente
  mensagem['To'] = destinatario
  mensagem['Reply-To'] = reply_to
  mensagem['Subject'] = "Aqui está o seu PIN de acesso"


  # Conectar ao servidor SMTP
  servidor_smtp = smtplib.SMTP('smtp.gmail.com', 587)
  servidor_smtp.starttls()
  servidor_smtp.login(remetente, senha)

  # Enviar o e-mail
  servidor_smtp.sendmail(remetente, destinatario, mensagem.as_string())

  # Encerrar a conexão
  servidor_smtp.quit()
  return pin