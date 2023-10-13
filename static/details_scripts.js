// ticketsDetails_data 
// commentsData
// emailsTransitData
const stateField = document.querySelector('.ticket_state');
const notification = document.querySelector('#total_interactions');
const createdBy = document.querySelector('.ticket_created');
const sendTo = document.querySelector('.ticket_mail');


document.addEventListener("DOMContentLoaded", function() {
  total_interactions = commentsData.length + 1
  notification.innerHTML = total_interactions
  addressData = emailsTransitData['MailAddress']
  console.log(addressData)
  for (var i = 0; i < addressData.length; i++) {
    switch(addressData[i]['Type']){
      case 'CC':
        continue
      case 'To':
        sendTo.innerHTML = "Enviado para: " + addressData[i]['Address'];
        break;
      case 'From':
        createdBy.innerHTML = "Criado por: " + addressData[i]['Address'];
        break;
    };
  };
  
});