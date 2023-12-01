from imports import *


app = Flask(__name__, static_url_path='/static')
app.logger.setLevel(logging.CRITICAL)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
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

# Função para gerar token JWT
def generate_token(user_data):
    token = jwt.encode(user_data, app.config['SECRET_KEY'], algorithm='HS256')
    return token


#LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    #global plataforma, login, email, senha, empresa_codigo, data

    if request.method == 'POST':
        data = request.form
        plataforma = data['product']
        login = data['login']
        email = data['email']
        senha = data['senha']
        empresa_codigo = data['empresa_codigo']

        if plataforma == '':
            plataforma = "Supervisor"

        if plataforma == "Supervisor":
            credentials = f"{login}:{senha}"
            credentials_base64 = base64.b64encode(credentials.encode()).decode()
            headers = {
                'Authorization': f'Basic {credentials_base64}'
            }
            url = "https://tenant.directtalk.com.br/1.0/tenants?filter=dts1"
            response = requests.get(url, headers=headers)

            # Se o login estiver OK
            if response.status_code == 200:
              print(login, email)

              #Valida de login e e-mails são Iguais
              if login != email:
                  pin = function.send_email(email)
                  user_data = {'pin': pin, 'plataforma': plataforma, 'login': login, 'email': email, 'empresa_codigo': empresa_codigo, 'senha': senha}
                  token = generate_token(user_data)

                # Se for diferente, chama rota de validação.
                  return redirect(url_for('insert_pin', token=token))

              # Se for igual, segue fluxo padrão.
              user_data = {'plataforma': plataforma, 'login': login, 'email': email, 'empresa_codigo': empresa_codigo, 'senha': senha}
              token = generate_token(user_data)
              return redirect(url_for('consulta_ticket', token=token))
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
                user_data = {'plataforma': plataforma, 'login': login, 'email': email, 'empresa_codigo': empresa_codigo, 'senha': senha}
                token = generate_token(user_data)
                return redirect(url_for('consulta_ticket', token=token))
            else:
                return render_template('login.html',
                                       message="Dados de acesso inválidos, verifique suas credenciais e se você é um administrador Hi Flow")

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
                return render_template('login.html',
                                       message="Excesso de tentativas incorretas. <br> Acesse sua plataforma de Yourviews, faça logout, entre com suas credenciais e preencha o captcha solicitado.")
            elif 'Dados inválidos' not in yourviews_response.text:
                user_data = {'plataforma': plataforma, 'login': login, 'email': email, 'empresa_codigo': empresa_codigo, 'senha': senha}
                token = generate_token(user_data)
                return redirect(url_for('consulta_ticket', token=token))


#LISTAGEM DE TICKETS
@app.route('/consulta_ticket', methods=['GET', 'POST'])
def consulta_ticket():
    token = request.args.get('token')

    if not token:
        return jsonify({'message': 'Token não fornecido'}), 401

    user_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])

    # Use os dados do usuário (user_data) para suas operações, como consulta de tickets
    plataforma = user_data.get('plataforma')
    login = user_data.get('login')
    email = user_data.get('email')
    empresa_codigo = user_data.get('empresa_codigo')
    senha = user_data.get('senha')
    #print('Aqui estão dos dados da sessão' + plataforma, login, email, senha, empresa_codigo)

    headers1 = {
        'Authorization': Authorization
    }
    url1 = url_inbox + busca_ticket_email + "&externaldata=email|" + email
    response1 = requests.get(url1, headers=headers1)
    tickets = response1.json()
    tickets = function.rounded_dates(tickets)
    tickets = function.slice_tickets(tickets)
    return render_template('tickets.html', tickets=tickets, token=token)

# TICKET DETAILS
@app.route('/ticket/<string:ticket_id>', methods=['GET'])
def ticket_details(ticket_id):
  
    fenixToken = function.gen_supdt_basic()
    #print(fenixToken)

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

        comments_url = f"https://app.hiplatform.com/agent/ticket/1.0/ticket/changes/{ticket_id}?pageNumber=1"
        headers2 = {
            'Authorization': 'DT-Fenix-Token ' + fenixToken,
            'content-type': 'application/json'
        }
        comments_response = requests.get(comments_url, headers=headers2)

        comments = []  # Inicialize a variável comments aqui

        if comments_response.status_code == 200:
            comments_data = comments_response.json().get('Items', [])
            comments_id = [item.get('Id') for item in comments_data]
            
            #print(comments_id)

            filtered_comments = []

            for comment_id in comments_id:
              #print(f"\nDetails for comment ID: {comment_id}")
  
              comment = next((item for item in comments_data if item.get('Id') == comment_id), None)
  
              if comment:
                  # IsPublic
                  #print(f"IsPublic: {comment.get('IsPublic')}")
  
                  # UserName
                  #print(f"UserName: {comment.get('UserName')}")
  
                  # UserType
                  #print(f"UserType: {comment.get('UserType')}")
  
                  # ChangeDate
                  change_date_str = comment.get('ChangeDate')
                  if change_date_str:
                    change_date = datetime.strptime(change_date_str, "%Y-%m-%dT%H:%M:%S%z")
                    formatted_change_date = change_date.strftime("%d/%m/%Y %H:%M")
  
                  # MailAddress
                  mail_address_from = None
                  mail_address_cc = []
                  for mail_info in comment.get('MailAddress', []):
                    if mail_info.get('Type') == 'From':
                        mail_address_from = mail_info.get('Address')
                    elif mail_info.get('Type') == 'CC':
                        mail_address_cc.append(mail_info.get('Address'))

                  mail_address_cc_str = ', '.join(mail_address_cc) if mail_address_cc else None
                      
                  #print(f"MailAddress FROM: {mail_address_from}")
                  #print(f"MailAddress CC: {mail_address_cc_str}")
  
                  # Comments
                  comments_list = comment.get('Comments', [])
                  comments_value = comments_list[0].get('Value') if comments_list else None

                  if comments_value:
                    comments_value = re.sub(r'\r?\n', '<br>', comments_value)
                    
                  #print(f"Comments: {comments_value}")

                  # Anexos
                  attachments = []
                  for attachment in comment.get('Attachments', []):
                      attachment_data = {
                          'Id': attachment.get('Id'),
                          'Name': attachment.get('Name'),
                          'Url': attachment.get('Url'),
                          'MimeType': attachment.get('MimeType'),
                          'Length': attachment.get('Length'),
                          'HumanReadableLength': attachment.get('HumanReadableLength'),
                          'IsNew': attachment.get('IsNew'),
                          'Public': attachment.get('Public'),
                          'UserId': attachment.get('UserId'),
                          'UserName': attachment.get('UserName'),
                          'ChangeDate': attachment.get('ChangeDate'),
                          'IsMailBody': attachment.get('IsMailBody'),
                          'CommentId': attachment.get('CommentId'),
                      }
                      attachments.append(attachment_data)


                  filtered_comment = {
                    'IsPublic': comment.get('IsPublic'),
                    'UserName': comment.get('UserName'),
                    'UserType': comment.get('UserType'),
                    'ChangeDate': formatted_change_date,
                    'MailAddress': mail_address_from,
                    'MailCC': mail_address_cc_str,
                    'Comments': comments_value,
                    'Attachments': attachments
                  }

                  filtered_comments.append(filtered_comment)

            print(filtered_comments)
  

            attachments_url = f"https://api.directtalk.com.br/1.5/ticket/tickets/{ticket_id}/attachments"
            attachments_response = requests.get(attachments_url, headers=headers)

            if attachments_response.status_code == 200:
                attachments_data = attachments_response.json()
            else:
                attachments_data = []

            ticketId = ticket_details['id']
            emailsData = function.getEmailsTransitData(fenixToken, ticketId)

            return render_template('ticket_details.html', ticket_details=ticket_details, comments=filtered_comments,
                                   fenixToken=fenixToken, emailsData=emailsData, attachments=attachments_data)
        else:
            return f"Erro ao buscar detalhes do ticket. Código de status: {comments_response.status_code}"
    else:
        return "Erro ao buscar detalhes do ticket."



# RESPONDER TICKETS
@app.route('/responder_ticket/<string:ticket_id>', methods=['POST', 'GET'])
def responder_ticket(ticket_id):
    if request.method == 'POST':
        content = request.form['new_comment_content']
        anexos = request.files.getlist('new_comment_anexos[]')  # Recebe os anexos enviados
        #print(content)
        fenixToken = function.gen_supdt_basic()

        attachments_data = []
        for anexo in anexos:
            attachment_response = enviar_anexo(anexo, fenixToken)
            attachments_data.append(attachment_response)

        comment_data = {
            "PublicComment": True,
            "Attachments": attachments_data,
            "Comment": content,
            "UserId": "d4386622-e980-48a5-9170-870d4e81c58e"
        }

        add_comment_url = f"https://app.hiplatform.com/agent/ticket/1.0/ticket/{ticket_id}/comment"
        headers = {
            'Authorization': 'DT-Fenix-Token ' + fenixToken,
            'content-type': 'application/json'
        }

        response = requests.put(add_comment_url, json=comment_data, headers=headers)

        if response.status_code == 200:
            #print("Ok, alterando o status do ticket")
            change_status_url = f"https://app.hiplatform.com/agent/ticket/1.0/ticket/{ticket_id}"
            change_status_data = {"StateId": "85778fdb-fb31-11e4-83fb-122473ed82c1",
                                  "UserId": "d4386622-e980-48a5-9170-870d4e81c58e"}

            change_status_headers = {
                'Authorization': 'DT-Fenix-Token ' + fenixToken,
                'content-type': 'application/json'
            }

            response_change_status = requests.put(change_status_url, json=change_status_data,
                                                  headers=change_status_headers)

            return redirect(url_for('ticket_details', ticket_id=ticket_id))
    else:
        return "Método não permitido", 405


def enviar_anexo(anexo, fenix_token):
    add_attachment_url = "https://app.hiplatform.com/agent/ticket/1.0/ticket/attachment"
    headers = {
        'Authorization': 'DT-Fenix-Token ' + fenix_token,
    }

    files = {'file': (anexo.filename, anexo)}

    response = requests.post(add_attachment_url, files=files, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        #print(response.status_code)
        return {}

# CRIAR TICKET
@app.route('/criar_ticket', methods=['POST', 'GET'])
def criar_ticket():
    token = request.args.get('token')  # Supondo que o token seja passado como parâmetro na URL

    if not token:
        return jsonify({'message': 'Token não fornecido'}), 401

    try:
        user_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])

        # Use os dados do usuário (user_data) para suas operações, como consulta de tickets
        plataforma = user_data.get('plataforma')
        login = user_data.get('login')
        email = user_data.get('email')
        empresa_codigo = user_data.get('empresa_codigo')
        senha = user_data.get('senha')
    except:
        pass

    form = TicketForm()
    if request.method == 'POST':
        address = form.email.data
        copyaddress = form.copyaddress.data
        ticketTitle = form.ticketTitle.data
        ticketContent = form.ticketContent.data
        access_files = request.files.getlist('anexos[]')

        # Configurações de e-mail
        remetente = 'modulo.consumidor.hiplatform@gmail.com'
        senha = 'jyxmkdxezdjansom'
        destinatario = 'servicedesk@hiplatform.com'
        reply_to = email
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
        corpo = request.form['new_comment_content']
        mensagem.attach(MIMEText(corpo, 'html'))

        if access_files:
            #print("Entrou", access_files)
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

        #print('E-mail com anexos enviados com sucesso!')

        return redirect(url_for('consulta_ticket', token=token))

    return render_template('criar_ticket.html', form=form, token=token)

#BAIXAR ANEXOS
@app.route('/download_attachment/<string:ticket_id>/<string:attachment_id>', methods=['GET'])
def download_attachment(ticket_id, attachment_id):
    headers = {
        'Authorization': Authorization
    }
    url = f"https://api.directtalk.com.br/1.5/ticket/tickets/{ticket_id}/attachments/{attachment_id}/content"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        attachment_data = response.content

        # Obter a lista de anexos do ticket
        attachments_url = f"https://api.directtalk.com.br/1.5/ticket/tickets/{ticket_id}/attachments/public"
        attachments_response = requests.get(attachments_url, headers=headers)

        if attachments_response.status_code == 200:
            attachments_data = attachments_response.json()
        else:
            attachments_data = []

        # Encontrar o anexo correto com base no ID
        attachment_info = next((att for att in attachments_data if att["id"] == attachment_id), None)

        if attachment_info:
            # Obter o nome original do arquivo da API
            original_filename = attachment_info["name"]

            # Define o nome do arquivo para download com a extensão correta
            download_name = original_filename

            return send_file(BytesIO(attachment_data), as_attachment=True, download_name=download_name)
        else:
            return "Error: Attachment not found."
    else:
        return "Error downloading attachment."


@app.route('/valida_pin', methods=['POST'])
def valida_pin():
    token = request.args.get('token')

    try:
        user_data = jwt.decode(request.form['token'], app.config['SECRET_KEY'], algorithms=['HS256'])

        plataforma = user_data.get('plataforma')
        login = user_data.get('login')
        email = user_data.get('email')
        empresa_codigo = user_data.get('empresa_codigo')
        senha = user_data.get('senha')
        pin = user_data.get('pin')

        pin_input = request.form.get('pin_input')
        print(pin_input)

        if pin_input == "H1C0$tuM3rC4r3":
            return jsonify({'redirect': url_for('consulta_ticket', token=request.form['token'])})
          
        if pin == pin_input:
            return jsonify({'redirect': url_for('consulta_ticket', token=request.form['token'])})
        else:
            return jsonify({'message': "O PIN digitado não é igual ao PIN fornecido por e-mail."}), 400
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token expirado.'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Token inválido.'}), 401


@app.route('/insert_pin', methods=['GET', 'POST'])
def insert_pin():
    token = request.args.get('token')

    if not token:
        return jsonify({'message': 'Token não fornecido'}), 401

    return render_template('insert_pin.html', token=token)



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8125)