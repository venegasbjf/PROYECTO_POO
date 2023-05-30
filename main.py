from __future__ import annotations

import eel
from library import Library


def main():
    
    @eel.expose
    def iniciar_juego(game_id: int | str) -> None:
        libreria.steam.play_game(game_id)
    
    @eel.expose
    def actualizar_juegos_favoritos(juegos_favoritos: dict[str, int]):
        libreria.update_favorite_games(juegos_favoritos)
    
    @eel.expose
    def actualizar_juegos_eliminados(juegos_favoritos: dict[str, int]):
        libreria.update_favorite_games(juegos_favoritos)
    
    @eel.expose
    def crear_libreria(usuario: dict[str, str]):
        libreria = Library(usuario["steam_id"], usuario["steam_api_key"], usuario["steam_grid_api_key"])
        info_libreria = libreria.create_user_library()
        return info_libreria
        
    libreria = None
    
    eel.init("src")
    eel.start("views/login.html")

if __name__ == "__main__":
    main()
# 76561198941605330
# EA29ED634385FF016C0B0363F3F23D27
# da02ff927bc9816956aa864cf62ba4ba

