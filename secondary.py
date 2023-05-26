from __future__ import annotations

from library import Library


def main(usuario: dict[str, str]):
    
    def cerrar_sesion() -> None:
        libreria.sign_out()
        
    def actualizar_categorias(user_categories: dict[str, list[int]]) -> None:
        libreria.update_user_categories(user_categories)

    def cambiar_keys(apis_keys: dict[str, str]) -> None:
        libreria.change_apis_keys(apis_keys)
        
    def iniciar_juego(game_id: int) -> None:
        libreria.steam.play_game(game_id)
    
    libreria = Library(usuario["steam_id"], usuario["steam_api_key"], usuario["steam_grid_api_key"])
    
    info_libreria = libreria.create_user_library()
    
    iniciar_juego(105600)

if __name__ == "__main__":
    main({"steam_id": "76561198941605330", "steam_api_key": "EA29ED634385FF016C0B0363F3F23D27", "steam_grid_api_key": "da02ff927bc9816956aa864cf62ba4ba"})