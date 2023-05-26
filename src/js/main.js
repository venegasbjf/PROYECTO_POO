document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault();
  
    var steamid = document.getElementById('steamid').value;
    var steamApiKey = document.getElementById('steam_api_key').value;
    var steamGridApiKey = document.getElementById('steam_grid_api_key').value;
  
    // Aquí puedes verificar los valores ingresados y definir tus condiciones particulares
    if (steamid === 'valor1' && steamApiKey === 'valor2' && steamGridApiKey === 'valor3') {
      window.location.href = './index.html'; // Redirige a la vista index
    } else {
      alert('Credenciales incorrectas');
    }
  });
  