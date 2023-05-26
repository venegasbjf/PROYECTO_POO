from __future__ import annotations

import json
import os

from apis import SteamAPI, SteamGridAPI
from databases import GamesDatabase
from logger import logger
from typing import Iterable
from user import User


class LibraryDataManager:

    def __init__(self, steam_id: str, steam_api_key: str, steam_grid_api_key: str) -> None:
        self.__user = User(steam_id)
        self.__steam_api = SteamAPI(steam_api_key)
        self.__steam_grid_api = SteamGridAPI(steam_grid_api_key)
        self.__games_db = GamesDatabase()
        
    def write_user_json_file(self, file_name: str, file_data: dict) -> None:
        os.makedirs(self.__user.user_folder, exist_ok=True)
        file_path = os.path.join(self.__user.user_folder, file_name + ".json")

        try:
            with open(file_path, "w") as file:    
                json.dump(file_data, file, indent=5)

        except IOError as e:
            logger.info(repr(e))
            
    def sign(self, in_: bool) -> None:
        self.write_user_json_file("last", {"in": in_})
    
    def get_user_data(self) -> (dict[str, str] | None):
        try:
            user_data = self.__steam_api.get_player_summaries(self.__user.steam_id)

            if user_data is not None:
                self.change_apis_keys({"steam_api_key": self.__steam_api._api_key, "steam_grid_api_key": self.__steam_grid_api._api_key})
                self.write_user_json_file("user_data", user_data)
                return user_data

            logger.error("La respuesta no contiene información sobre la cuenta")
      
        except Exception as e:
            logger.error(repr(e))

        user_data = self.__read_user_json_file("user_data")
        
        return user_data
    
    def get_owned_games(self) -> (dict[int, str] | None):
        try:
            owned_games = self.__steam_api.get_owned_games(self.__user.steam_id)

            if owned_games is not None:
                self.write_user_json_file("owned_games", owned_games)
                return owned_games

            logger.error("La respuesta no contiene información sobre los juegos de la cuenta")

        except Exception as e:
            logger.error(repr(e))

        owned_games = self.__read_user_json_file("owned_games")
        
        return {int(steam_appid): name for steam_appid, name in owned_games.items()} if owned_games else None
    
    def get_games_data(self, owned_games: dict[int, str]) -> tuple[dict[int, dict[str]], dict[str, list[int]], dict[str, list[int]]]:
        games_data = self.__games_db.get_games(owned_games)
        requested_games = self.__steam_api.get_apps_details((steam_appid for steam_appid in owned_games if steam_appid not in games_data), owned_games)

        self.__games_db.add_games({app_id: game.copy() for app_id, game in requested_games.items()})
        games_data.update(requested_games)

        categories = self.__get_user_categories(games_data, requested_games)
        genres = self.__get_user_genres(games_data, requested_games)
        
        return games_data, categories, genres
            
    def change_apis_keys(self, apis_keys: dict[str, str]) -> None:
        self.__steam_api._api_key = apis_keys["steam_api_key"]
        self.__steam_grid_api._api_key = apis_keys["steam_grid_api_key"]
        self.write_user_json_file("api_keys", apis_keys)
        
    def get_images(self, owned_games: dict[int, str]) -> None:
        images = self.__games_with_images(owned_games)

        try:
            for steam_appid in owned_games:  

                if steam_appid not in images["library_600x900_2x"]:
                    self.__get_grid(steam_appid)

                if steam_appid not in images["library_hero"]:
                    self.__get_heroe(steam_appid)

        except Exception as e:
            logger.error(repr(e))
                
    def __get_grid(self, steam_appid: int) -> None:
        grid = self.__steam_api.get_grid(steam_appid)
        grid = self.__steam_grid_api.get_grid(steam_appid) if not grid else grid

        if grid:
            grid_bytes, file_type = grid
            self.__write_image_bytes(steam_appid, grid_bytes,"library_600x900_2x", file_type)
            
    def __get_heroe(self, steam_appid: int) -> None:
        heroe = self.__steam_api.get_heroe(steam_appid)
        heroe = self.__steam_grid_api.get_heroe(steam_appid) if not heroe else heroe
        
        if heroe:
            heroe_bytes, file_type = heroe
            self.__write_image_bytes(steam_appid, heroe_bytes, "library_hero", file_type)
    
    def __games_with_images(self, steam_apps_ids: Iterable[int]) -> dict[str, set[int]]:
        images_folder_path = os.path.join("library", "images")
        accepted_file_types = {".jpg", ".png", ".webp"}
        
        images = {"library_600x900_2x": set(), "library_hero": set()}

        if os.path.exists(images_folder_path): 
            for steam_appid in steam_apps_ids:
                game_folder = os.path.join(images_folder_path, str(steam_appid))
                
                if not os.path.exists(game_folder):
                    continue
                    
                for file in os.listdir(game_folder):
                    name, file_type = os.path.splitext(file)
                            
                    if name in images and file_type in accepted_file_types:
                        images[name].add(steam_appid)
                        
        return images
    
    def __write_image_bytes(self, steam_appid: int, image_bytes: bytes, file_name: str, file_type: str) -> None:
        game_folder_path = os.path.join("library", "images", str(steam_appid))
        os.makedirs(game_folder_path, exist_ok=True)
        
        image_path = os.path.join(game_folder_path, file_name + "." + file_type)
        
        try:
            with open(image_path, "wb") as image:
                image.write(image_bytes)
                
        except IOError as e:
            logger.error(repr(e))
            
    def __read_user_json_file(self, file_name: str) -> (dict | None):
        file_path = os.path.join(self.__user.user_folder, file_name + ".json")
        
        try:
            with open(file_path) as file:
                return json.load(file)
                
        except IOError as e:
            logger.info(repr(e))
            
    def __get_user_categories(self, games_data: dict[int, dict[str]], requested_games: dict[int, dict[str]]) -> dict[str, list[int]]:
        user_categories = self.__read_user_json_file("user_categories")
        new_games, user_categories = (games_data, {}) if user_categories is None else (requested_games, user_categories)
        
        for game_data in new_games.values():
            for categorie in game_data["categories"]:
                
                if user_categories.get(categorie) is None:
                    user_categories[categorie] = []
                    
        for steam_appid, game_data in new_games.items(): 
            for categorie in game_data["categories"]:  
                user_categories[categorie].append(steam_appid)
                    
        self.write_user_json_file("user_categories", user_categories)
                    
        return user_categories
    
    def __get_user_genres(self, games_data: dict[int, dict[str]], requested_games: dict[int, dict[str]]) -> dict[str, list[int]]:
        user_genres = self.__read_user_json_file("user_genres")
        new_games, user_genres = (games_data, {}) if user_genres is None else (requested_games, user_genres)
        
        for game_data in new_games.values():
            for genre in game_data["genres"]:
                
                if user_genres.get(genre) is None:
                    user_genres[genre] = []
                    
        for steam_appid, game_data in new_games.items():
            for genre in game_data["genres"]:
                user_genres[genre].append(steam_appid)
                    
        self.write_user_json_file("user_genres", user_genres)
                    
        return user_genres