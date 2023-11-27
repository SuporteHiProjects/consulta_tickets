// ticketsDetails_data 
// commentsData
// emailsTransitData
const stateField = document.querySelector('.ticket_state');
const notification = document.querySelector('#total_interactions');
const createdBy = document.querySelector('.ticket_created');
const sendTo = document.querySelector('.ticket_mail');
const returnButton = document.querySelector('#back-button');
const addNewComment = document.querySelector('#add_new_comment');
const creation_first_msg = document.querySelector("#creation_user_msg");

document.addEventListener("DOMContentLoaded", function() {
  returnButton.textContent = '<<'
  var total_interactions = 1;
  for (comment of commentsData){
    if(comment.IsPublic == true){
      total_interactions = total_interactions + 1
    }
  }
  notification.innerHTML = total_interactions
  addressData = emailsTransitData['MailAddress']
  for (var i = 0; i < addressData.length; i++) {
    switch(addressData[i]['Type']){
      case 'CC':
        continue
      case 'To':
        sendTo.innerHTML = "Enviado para: " + addressData[i]['Address'];
        break;
      case 'From':
        createdBy.innerHTML = "Criado por: " + addressData[i]['Address'];
        creation_first_msg.innerHTML = addressData[i]['Address']
        break;
    };
  };
  
});

document.addEventListener('DOMContentLoaded', function () {
  var attachmentsButton = document.getElementById('attachmentsButton');
  var attachmentsModal = new bootstrap.Modal(document.getElementById('attachmentsModal'));

  attachmentsButton.addEventListener('click', function () {
    attachmentsModal.show();
  });

  attachmentsModal._element.addEventListener('hidden.bs.modal', function () {
    document.activeElement.blur();
  });
});
  
document.addEventListener('DOMContentLoaded', function () {
      var addCommentButton = document.getElementById('add_new_comment');
      if (addCommentButton && addCommentButton.disabled) {
          new bootstrap.Tooltip(addCommentButton);
      }
  });