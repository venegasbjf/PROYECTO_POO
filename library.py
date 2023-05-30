from __future__ import annotations

from library_data_manager import LibraryDataManager
from steam import Steam


class Library:
    
    def __init__(self, steam_id: str, steam_api_key: str, steam_grid_api_key: str) -> None:
        self.__data_manager: LibraryDataManager = LibraryDataManager(steam_id, steam_api_key, steam_grid_api_key)
        self.__steam: Steam = Steam()
        
    def create_user_library(self) -> dict[str]:
        user_data = self.__data_manager.get_user_data()
        
        if user_data is None:
            return {"response": "account information error"}
        
        owned_games = self.__data_manager.get_owned_games()
        
        if owned_games is None:
            return {"response": "error games account"}
        
        library_data = {"response": "success", "user_data": user_data}
        
        library_data.update(self.__data_manager.get_games_data(owned_games))
        library_data.update(self.__steam.is_steam_installed())

        self.__data_manager.get_images(library_data["games_data"])
        
        self.__data_manager.write_user_json_file("data", library_data)
        
        return library_data
    
    def update_favorite_games(self, favorite_games: dict[str, int]) -> None:
        self.__data_manager.write_user_json_file("favorite_games", favorite_games)
    
    def update_eliminated_games(self, eliminated_games: dict[str, int]) -> None:
        self.__data_manager.write_user_json_file("eliminated_games", eliminated_games)
        
    @property
    def steam(self):
        return self.__steam