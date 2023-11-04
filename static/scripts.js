const loading_button = document.querySelector('#loading_button');
const ticketDetails_button = document.querySelector('.list-group');
const ticket_cards = document.querySelectorAll('.list-group');
// ticketsData 
const tabLinks = document.querySelectorAll('.nav-link');
const prevPageBtn = document.getElementById('prevPage');
const nextPageBtn = document.getElementById('nextPage');
const progressBar = document.querySelector('.progressBar_details');

const itemsPerPage = 3;
let currentPage = 0;

document.addEventListener("DOMContentLoaded", function () {
  
  var countTickets = document.querySelectorAll(".list-group.ticket-list[data-tab='waiting-tickets']").length;
  if(countTickets == 0){
    document.querySelector('#nav-waitingTickets-tab').style.display = 'none';
  }
  document.querySelector('#waiting_count').innerHTML = countTickets;
    });

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
  prevPageBtn.style.display = 'none';
  nextPageBtn.style.display = 'none';
  progressBar.style.display = 'block';
  window.location.href = `/ticket/${ticketId}`;
        }

function createNewTicket(){
  prevPageBtn.style.display = 'none';
  nextPageBtn.style.display = 'none';
  progressBar.style.display = 'block';
  window.location.href = `/criar_ticket`;
}