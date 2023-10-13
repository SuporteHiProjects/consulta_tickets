import datetime
import time
import json
import time
import pytz
import requests

def generateFenixToken():
  url = "https://www3.directtalk.com.br/adminuiservices/api/Login"
  payload = "{}"
  headers = {
  'Accept': 'application/json, text/plain, */*',
  'Connection': 'keep-alive',
  'Content-Type': 'application/json; charset=UTF-8',
  'Authorization': 'Basic ZHRzMXdpbGxpYW0ud2VpZGdlbmFuZDozNDY2MTE3V3c='
  }
  response = requests.request("POST", url, headers=headers, data=payload)
  tokenData = response.json()
  token = tokenData['token']
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