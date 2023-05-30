from __future__ import annotations

import json
import os

from apis import SteamAPI, SteamGridAPI
from databases import GamesDatabase
from logger import logger
from typing import Iterable, Any
from user import User


class LibraryDataManager:

    def __init__(self, steam_id: str, steam_api_key: str, steam_grid_api_key: str) -> None:
        self.__user: User = User(steam_id)
        self.__steam_api: SteamAPI = SteamAPI(steam_api_key)
        self.__steam_grid_api: SteamGridAPI = SteamGridAPI(steam_grid_api_key)
        self.__games_db: GamesDatabase = GamesDatabase()
        
    def get_user_data(self) -> (dict[str, str] | None):
        try:
            user_data = self.__steam_api.get_player_summaries(self.__user.steam_id)
            
            if user_data is not None:
                self.write_user_json_file("user_data", user_data)
                return user_data
            
            logger.error(f"No se pudo conseguir información sobre la cuenta {self.__user} desde la API de Steam")
            
        except Exception as e:
            logger.error(f"Ocurrio un error mientras se obtenia la informacion de la cuenta {self.__user} desde la API de Steam")
        
        user_data = self.__read_user_json_file("user_data", None)
        
        return user_data
    
    def get_owned_games(self) -> (dict[int, str] | None):
        try:
            owned_games = self.__steam_api.get_owned_games(self.__user.steam_id)
            
            if owned_games is not None:
                self.write_user_json_file("owned_games", owned_games)
                return owned_games
            
            logger.error(f"No se pudo conseguir la lista de juegos de la cuenta {self.__user} desde la API de Steam")
            
        except Exception as e:
            logger.error(f"Ocurrio un error mientras se obtenia la lista de juegos de la cuenta {self.__user} desde la API de Steam")
        
        owned_games = self.__read_user_json_file("owned_games", None)
        owned_games = {int(steam_appid): name for steam_appid, name in owned_games.items()} if owned_games else None
        
        return owned_games
    
    def get_games_data(self, owned_games: dict[int, str]) -> dict[str, dict]:
        games_dict = {"games_data": self.__games_db.get_games(owned_games)}
        
        requested_games_data = self.__steam_api.get_apps_details((steam_appid for steam_appid in owned_games if steam_appid not in games_dict["games_data"]), owned_games)
        self.__games_db.add_games(requested_games_data)
        
        games_dict["games_data"].update(requested_games_data)
        games_dict["categories"] = self.__summarize_game_classifications(games_dict["games_data"], "categories")
        games_dict["genres"] = self.__summarize_game_classifications(games_dict["games_data"], "genres")
        games_dict["favorite_games"] = self.__read_user_json_file("favorite_games", {})
        games_dict["eliminated_games"] = self.__read_user_json_file("eliminated_games", {})
        
        return games_dict
    
    def get_images(self, owned_games: dict[int, str]) -> None:
        images = self.__games_with_images(owned_games)
        
        try:
            for steam_appid in owned_games:
                
                if steam_appid not in images["library_600x900_2x"]:
                    self.__get_grid(steam_appid)
                
                if steam_appid not in images["library_hero"]:
                    self.__get_heroe(steam_appid)
        
        except Exception as e:
            logger.error(f"Se perdio la conexion mientras se conseguian las imagenes de los juegos de la cuenta {self.__user}")
    
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
    
    def __write_image_bytes(self, steam_appid: int, image_bytes: bytes, file_name: str, file_type: str) -> None:
        game_folder_path = os.path.join("src", "images", str(steam_appid))
        os.makedirs(game_folder_path, exist_ok=True)
        image_path = os.path.join(game_folder_path, file_name + "." + file_type)
        
        try:
            with open(image_path, "wb") as image:
                image.write(image_bytes) 
        
        except IOError as e:
            logger.error(f"Ocurrio un error mientras se escribian los bits de la imagen {file_name} del juego {steam_appid}") 
            
    def __games_with_images(self, steam_apps_ids: Iterable[int]) -> dict[str, set[int]]:
        images_folder_path = os.path.join("src", "images")
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
    
    def __summarize_game_classifications(self, games_data: dict[int, dict[str]], classification_type: str) -> dict[str, list[int]]:
        classifications = {}
        
        for game_data in games_data.values():
            for classification in game_data[classification_type]:
                classifications[classification] = []
             
        for steam_appid, game_data in games_data.items(): 
            for classification in game_data[classification_type]:  
                classifications[classification].append(steam_appid)
        
        return classifications
    
    def __read_user_json_file(self, file_name: str, default_value) -> (dict | Any):
        file_path = os.path.join(self.__user.user_folder, file_name + ".json")
        
        try:
            with open(file_path) as file:
                return json.load(file)   
         
        except IOError as e:
            logger.info(f"No se pudo leer el archivo {file_name}")
            
        return default_value
    
    def write_user_json_file(self, file_name: str, file_data: dict) -> None:
        os.makedirs(self.__user.user_folder, exist_ok=True)
        file_path = os.path.join(self.__user.user_folder, file_name + ".json")
        
        try:
            with open(file_path, "w") as file:    
                json.dump(file_data, file, indent=5)

        except IOError as e:
            logger.info(f"No se pudo escribir el archivo {file_name}")