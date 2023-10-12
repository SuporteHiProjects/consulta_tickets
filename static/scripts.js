const loading_button = document.querySelector('#loading_button');
const ticketDetails_button = document.querySelector('.list-group');
const ticket_cards = document.querySelectorAll('.list-group');
// ticketsData -> var com todos os dados que chegam do jinja, pra ser usado aqui no js
// ticketsDetails_data -> var com todos os dados que chegam do jinja a respeito do ticketdetails
const tabLinks = document.querySelectorAll('.nav-link');
const prevPageBtn = document.getElementById('prevPage');
const nextPageBtn = document.getElementById('nextPage');
const stateField = document.querySelector('.ticket_state');
const itemsPerPage = 2;
let currentPage = 0;

function showPage(page) {
  const visibleTickets = currentTabContent.querySelectorAll('.list-group.ticket-list');
  visibleTickets.forEach((ticket, index) => {
    if (index >= page * itemsPerPage && index < (page + 1) * itemsPerPage) {
      ticket.style.display = 'block';
    } else {
      ticket.style.display = 'none';
    }
  });
}

function updatePageButtons() {
  if (currentPage === 0) {
    prevPageBtn.disabled = true;
  } else {
    prevPageBtn.disabled = false;
  }

  const visibleTickets = currentTabContent.querySelectorAll('.list-group.ticket-list');
  if ((currentPage + 1) * itemsPerPage >= visibleTickets.length) {
    nextPageBtn.disabled = true;
  } else {
    nextPageBtn.disabled = false;
  }
}

function initializeTab(tabLink) {
  const tabContentID = tabLink.getAttribute('data-bs-target');
  currentTabContent = document.querySelector(tabContentID);
  currentPage = 0;
  showPage(currentPage);
  updatePageButtons();
}

tabLinks.forEach((tabLink) => {
  tabLink.addEventListener('click', (event) => {
    event.preventDefault();
    initializeTab(tabLink);
  });
});

prevPageBtn.addEventListener('click', () => {
  if (currentPage > 0) {
    currentPage--;
    showPage(currentPage);
    updatePageButtons();
  }
});

nextPageBtn.addEventListener('click', () => {
  const visibleTickets = currentTabContent.querySelectorAll('.list-group.ticket-list');
  if ((currentPage + 1) * itemsPerPage < visibleTickets.length) {
    currentPage++;
    showPage(currentPage);
    updatePageButtons();
  }
});

initializeTab(tabLinks[0]);

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
