document.getElementById('loginForm').addEventListener('submit', async function(event) {
    event.preventDefault();
  
    let steamid = document.getElementById('steamid').value;
    let steamApiKey = document.getElementById('steam_api_key').value;
    let steamGridApiKey = document.getElementById('steam_grid_api_key').value;

    //alert("Creando libreria, espere un momento...")

    let data = await eel.crear_libreria({"steam_id": steamid, "steam_api_key": steamApiKey, "steam_grid_api_key": steamGridApiKey})();
    
    if (data["response"] == "success") {
        window.location.href = './index.html'; // Redirige a la vista index
    } else {
        alert(data["response"]);
    }

  });