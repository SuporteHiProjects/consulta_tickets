const loginButton = document.querySelector('#login_button');

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