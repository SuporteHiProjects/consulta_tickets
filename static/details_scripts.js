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
  showAttachments()
  validateAccordeonDetails()
  validateCommentSender()
  setInteractionsNotifications()
  checkAndFixEmailsTransitData()
  returnButton.textContent = '<<'
  document.querySelector('#isPasted').style.whiteSpace = 'inherit';
  var addCommentButton = document.getElementById('add_new_comment');
  if (addCommentButton && addCommentButton.disabled) {
      new bootstrap.Tooltip(addCommentButton);
  }
  var gmail_contents = document.getElementsByTagName("table");
  while (gmail_contents[0]) {
       gmail_contents[0].parentNode.removeChild(gmail_contents[0]);
  };
});

function showAttachments(){
  var attachmentsButton = document.getElementById('attachmentsButton');
  var attachmentsModal = new bootstrap.Modal(document.getElementById('attachmentsModal'));

  attachmentsButton.addEventListener('click', function () {
    attachmentsModal.show();
  });

  attachmentsModal._element.addEventListener('hidden.bs.modal', function () {
    document.activeElement.blur();
  });
}

function validateAccordeonDetails() {
  var detailsButton = document.getElementById('detailsButton');
  var collapseThree = document.getElementById('collapseThree');
  var isDetailsExpanded = localStorage.getItem('detailsExpanded') === 'true';
  if (isDetailsExpanded) {
      collapseThree.classList.add('show');
  }
  detailsButton.addEventListener('click', function () {
      localStorage.setItem('detailsExpanded', !collapseThree.classList.contains('show'));
  });
};

function validateCommentSender() {
  var submitButton = document.getElementById('submitCommentBtn');
  var form = document.querySelector('form');

  if (form) {
    form.addEventListener('submit', function (event) {
      var commentContent = document.getElementById('textArea_content').value;
      var commentContentWithBr = commentContent.replace(/\r?\n/g, "<br>");
      var hiddenInput = document.createElement('input');
      hiddenInput.type = 'hidden';
      hiddenInput.name = 'new_comment_content_with_br';
      hiddenInput.value = commentContentWithBr;
      form.appendChild(hiddenInput);

      submitButton.disabled = true;

      setTimeout(function () {
        submitButton.disabled = false;
        location.reload();
      }, 9000);
    });
  }
}


function setInteractionsNotifications() {
  var total_interactions = 1;
  for (comment of commentsData) {
    if(comment.IsPublic == true) {
      total_interactions = total_interactions + 1;
    };
  };
  notification.innerHTML = total_interactions;
};

function checkAndFixEmailsTransitData() {
  addressData = emailsTransitData['MailAddress']
  for (var i = 0; i < addressData.length; i++) {
    switch(addressData[i]['Type']){
      case 'CC':
        continue;
      case 'To':
        sendTo.innerHTML = '<i class="fa-regular fa-envelope"></i> Enviado para: ' + addressData[i]['Address'];
        break;
      case 'From':
        createdBy.innerHTML = '<i class="fa-solid fa-address-card"></i> Criado por: ' + addressData[i]['Address'];
        creation_first_msg.innerHTML = 'Ticket criado por: ' + addressData[i]['Address'];
        break;
    }
  }
}
