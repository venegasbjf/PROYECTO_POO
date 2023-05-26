from __future__ import annotations

from library_data_manager import LibraryDataManager
from steam import Steam


class Library:
    
    def __init__(self, steam_id: str, steam_api_key: str, steam_grid_api_key: str) -> None:
        self.__data_manager = LibraryDataManager(steam_id, steam_api_key, steam_grid_api_key)
        self.__steam = Steam()
        
    def create_user_library(self) -> (tuple[str, dict[str, str], dict[int, dict[str]], dict[str, list[int]], dict[str, list[int]], tuple[bool, list[int]]] | tuple[str]):
        user_data = self.__data_manager.get_user_data()
        
        if user_data is None:
            return ("Error usuario")
        
        owned_games = self.__data_manager.get_owned_games()
        
        if owned_games is None:
            return ("Error juegos usuario")
        
        games, categories, genres = self.__data_manager.get_games_data(owned_games)
        
        self.__data_manager.write_user_json_file("user_games", games)
        
        steam_data = self.__steam.steam_data()
        steam_data["installed_games"] = [appid for appid in steam_data["installed_games"] if appid in games]
            
        self.__data_manager.get_images(games)
        
        self.__data_manager.sign(True)
        
        return "Ok", user_data, games, categories, genres, steam_data
    
    def change_apis_keys(self, apis_keys: dict[str, str]) -> None:
        self.__data_manager.change_apis_keys(apis_keys)
        
    def update_user_categories(self, user_categories: dict[str, list[int]]):
        self.__data_manager.write_user_json_file("user_categories", user_categories)
    
    def sign_out(self) -> None:
        self.__data_manager.sign(False)
        
    @property
    def steam(self):
        return self.__steam