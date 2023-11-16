const loginButton = document.querySelector('#login_button');
const empresaCodigoInput = document.getElementById('empresa_codigo');
const plataformaSocialInput = document.getElementById('plataforma_social');
const loginLabelInput = document.getElementById('login_label');
const emailLabelInput = document.getElementById('email_label');
const pwdLabelInput = document.getElementById('pwd_label');
let inputTimer;

loginLabelInput.addEventListener('blur', function() {
  if(loginLabelInput.value != '') {
  clearTimeout(inputTimer);
  inputTimer = setTimeout(function() {
      if (!validateEmail(loginLabelInput.value)) {
          document.getElementById('email_label').style.display = 'none';
          emailLabelInput.value = loginLabelInput.value
          console.log(emailLabelInput.value)
      } else {
          document.getElementById('email_label').style.display = 'block';
      }
  }, 200);
}
  else {
        document.getElementById('email_label').style.display = 'none';
    }
});

function validateEmail(email) {
  const regex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/;
  return !regex.test(String(email).toLowerCase());
}

$(document).ready(function(){
  $('[data-bs-toggle="tooltip"]').tooltip();
});

document.addEventListener('DOMContentLoaded', function () {
    empresaCodigoInput.style.display = 'None';
    plataformaSocialInput.style.display = 'None';
    loginLabelInput.style.display = 'block';
    emailLabelInput.style.display = 'none';
    pwdLabelInput.style.display = 'block';
    const navItems = document.querySelectorAll('.nav-item li');
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            if(item.innerHTML != "HiSocial"){
              navItems.forEach(i => i.classList.remove('active'));
              item.classList.add('active');
            }
        });
    });
});

loginButton.addEventListener('click', () => {
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

function buttonClicked(button) {
  const buttons = document.querySelectorAll('.nav-item li');
  buttons.forEach(btn => btn.classList.remove('active'));
  button.classList.add('active');
  const loginValue = button.textContent;
  if(loginLabelInput.value === ''){
    emailLabelInput.style.display = 'none';
  }
  switch(loginValue){
    case "Supervisor":
      empresaCodigoInput.style.display = 'None';
      plataformaSocialInput.style.display = 'None';
      loginLabelInput.style.display = 'block';
      pwdLabelInput.style.display = 'block';
      var form = document.getElementById("form_login")
      form.reset()
      document.getElementById('selected_product').value = loginValue;
      break
    case "HiSocial":
      null
      //empresaCodigoInput.style.display = 'None';
      //plataformaSocialInput.style.display = 'block';
      //loginLabelInput.style.display = 'None';
      //emailLabelInput.style.display = 'block';
      //pwdLabelInput.style.display = 'block';
      //var form = document.getElementById("form_login")
      //form.reset()
      //document.getElementById('selected_product').value = loginValue;
      break
    case "HiFlow":
      empresaCodigoInput.style.display = 'block';
      plataformaSocialInput.style.display = 'None';
      loginLabelInput.style.display = 'None';
      emailLabelInput.style.display = 'block';
      pwdLabelInput.style.display = 'block';
      var form = document.getElementById("form_login")
      form.reset()
      document.getElementById('selected_product').value = loginValue;
      break
    case "Yourviews":
      empresaCodigoInput.style.display = 'None';
      plataformaSocialInput.style.display = 'None';
      loginLabelInput.style.display = 'None';
      emailLabelInput.style.display = 'block';
      pwdLabelInput.style.display = 'block';
      var form = document.getElementById("form_login")
      form.reset()
      document.getElementById('selected_product').value = loginValue;
      break
  }
};
