document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault();
  
    var steamid = document.getElementById('steamid').value;
    var steamApiKey = document.getElementById('steam_api_key').value;
    var steamGridApiKey = document.getElementById('steam_grid_api_key').value;
  
    // Aquí puedes verificar los valores ingresados y definir tus condiciones particulares
    if (steamid === '76561198941605330' && steamApiKey === 'EA29ED634385FF016C0B0363F3F23D27' && steamGridApiKey === 'da02ff927bc9816956aa864cf62ba4ba') {
      window.location.href = './index.html'; // Redirige a la vista index
    } else {
      alert('Credenciales incorrectas');
    }
  });
  