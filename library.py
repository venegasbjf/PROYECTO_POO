from __future__ import annotations

from library_data_manager import LibraryDataManager
from steam import Steam


class Library:
    
    def __init__(self, steam_id: str, steam_api_key: str, steam_grid_api_key: str) -> None:
        self.__data_manager = LibraryDataManager(steam_id, steam_api_key, steam_grid_api_key)
        self.__steam = Steam()
        
    def create_user_library(self) -> tuple[dict[str, str], dict[int, dict[str]], dict[str, list[int]], dict[str, list[int]]]:
        user_data = self.__data_manager.get_user_data()
        
        if user_data is None:
            raise Exception("Error usuario")
        
        owned_games = self.__data_manager.get_owned_games()
        
        if owned_games is None:
            raise Exception("Error juegos usuario")
        
        games, categories, genres = self.__data_manager.get_games_data(owned_games)
            
        self.__data_manager.get_images(games)
        
        self.__data_manager.mark_account(True)
        
        return user_data, games, categories, genres
    
    def change_apis_keys(self, steam_api_key: str, steam_grid_api_key: str) -> None:
        self.__data_manager.change_api_keys(steam_api_key, steam_grid_api_key)
        
    def sign_out(self) -> None:
        self.__data_manager.mark_account(False)