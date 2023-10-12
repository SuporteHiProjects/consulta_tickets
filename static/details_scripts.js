// ticketsDetails_data 
// commentsData
const stateField = document.querySelector('.ticket_state');
const notification = document.querySelector('#total_interactions');


document.addEventListener("DOMContentLoaded", function() {
  total_interactions = commentsData.length + 1
  notification.innerHTML = total_interactions
});