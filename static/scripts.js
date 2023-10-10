const loginButton = document.querySelector('#login_button');
const loading_button = document.querySelector('#loading_button');
const ticketDetails_button = document.querySelector('.list-group');
const ticket_cards = document.querySelectorAll('.list-group');
const ticket_identity = document.querySelectorAll('p.ticket_identity');

function printSelectedTabRecords(tabName) {
    var selectedRecords = $(".ticket-list[data-tab='" + tabName + "']");
    selectedRecords.each(function(index, element) {
        console.log(element)
    });
}

$(".nav-link").click(function() {
    var tabId = $(this).attr("aria-controls");
    var tabName = $("#" + tabId + " .ticket-list:first").data("tab");
    printSelectedTabRecords(tabName);
});

$(document).ready(function() {
    $(".ticket-list").show();
    $(".nav-link").click(function() {
        $(".ticket-list").hide();
        var tabId = $(this).attr("aria-controls");
        $("#" + tabId + " .ticket-list").show();
    });
});

loginButton.addEventListener('click', () => {
  console.log("TESTE")
  loginButton.style.display = 'none';
  loading_button.style.display = 'block';
  var loginLabel = document.getElementById('login_label').value;
  var emailLabel = document.getElementById('email_label').value;
  var pwdLabel = document.getElementById('pwd_label').value;
  if(loginLabel == '' || emailLabel == '' || pwdLabel == ''){
    setTimeout(() => {
      loading_button.style.display = 'none';
      loginButton.style.display = 'block';
    }, 200);
  }
})

function redirectToTicketDetails(ticketId) {
            window.location.href = `/ticket/${ticketId}`;
        }

window.addEventListener('load', function() {
        const urlParts = window.location.pathname.split('/');
        const ticketId = urlParts[urlParts.length - 1];

        console.log('ID do Ticket:', ticketId);
        if (ticketId) {
            loadTicketComments(ticketId);
        }
    });

    function loadTicketComments(ticketId) {
        const commentsUrl = `https://api.directtalk.com.br/1.5/ticket/tickets/${ticketId}/comments/public`;
        const authHeader = 'Basic ZHRzMTg2ZTIzYWNkLTBiZDYtNGE4YS1iNTFlLWNiOGIzMWExZmI2ZTpkdnZic2tobTZhdHd0OWVscGNzdg==';
        fetch(commentsUrl, {
            headers: {
                'Authorization': authHeader
            }
        })
        .then(response => response.json())
        .then(comments => {
            const commentsContainer = document.getElementById('comments-container');
            commentsContainer.innerHTML = '';
            const commentsArray = comments;
            commentsArray.reverse();
            commentsArray.forEach(comment => {
                const commentBlock = document.createElement('div');
                commentBlock.classList.add('comment-block');

                const authorAndDate = document.createElement('p');
                authorAndDate.classList.add('comment-author-date');
                authorAndDate.textContent = `${comment.user.name} escreveu em ${new Date(comment.date * 1000).toLocaleString('pt-BR', { timeZone: 'America/Sao_Paulo' })}`;

                const content = document.createElement('p');
                content.classList.add('comment-content');
                content.innerHTML = comment.content;

                commentBlock.appendChild(authorAndDate);
                commentBlock.appendChild(content);
                commentsContainer.appendChild(commentBlock);
            });
        })
        .catch(error => console.error('Erro ao buscar comentários: ', error));
    }