$('#create_button').on('click', function() {
 $('body').addClass('modal-open');
 $('#loadingModal').modal('show');
});

$(document).on('show.bs.modal', '.modal', function () {
 $(this).appendTo('body');
}).on('shown.bs.modal', '.modal.in', function() {
 $('body').addClass('modal-open');
}).on('hidden.bs.modal', '.modal', function() {
 $('body').removeClass('modal-open');
});

$('#form').on('submit', function() {
 $('#loadingModalLabel').text('Ticket criado com sucesso');
 $('.fa-spinner').remove();
});

setTimeout(function() {
 $('body').removeClass('modal-open');
 $('#loadingModal').modal('hide');
}, 2000);
