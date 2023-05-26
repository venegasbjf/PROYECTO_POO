from __future__ import annotations

import os
import sqlite3

from abc import ABC
from typing import Iterable

class Database(ABC):
    
    def __init__(self, table_name: str, columns_type: dict[str, str]) -> None:
        
        self.__database_folder_path = os.path.join("library", "data")
        self.__database_path = os.path.join(self.__database_folder_path , table_name + ".db")
        
        self.__create_table = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join([f'{column} {datatype}' for column, datatype in columns_type.items()])})"
        self.__select_row = f"SELECT * FROM {table_name} WHERE {next(iter(columns_type))} = ?"
        self.__insert_row = f"INSERT INTO {table_name} ({', '.join(columns_type)}) VALUES ({', '.join('?' for _ in range(len(columns_type)))})"
        
    def _get_row(self, primary_key_value) -> tuple | None:
        self.__cursor.execute(self.__select_row, (primary_key_value,))
        return self.__cursor.fetchone()
    
    def _add_row(self, row_values: tuple) -> None:
        self.__cursor.execute(self.__insert_row, row_values)
        self.__conn.commit()
        
    def _connect(self) -> None:
        os.makedirs(self.__database_folder_path, exist_ok=True)
        self.__conn = sqlite3.connect(self.__database_path)
        self.__cursor = self.__conn.cursor()
        self.__cursor.execute(self.__create_table)
    
    def _close(self) -> None:
        self.__conn.close()


class GamesDatabase(Database):

    def __init__(self) -> None:
        super().__init__("GamesDatabase", 
                         {"steam_appid": "INTEGER PRIMARY KEY", 
                          "description": "TEXT", 
                          "developers": "TEXT", 
                          "publishers": "TEXT", 
                          "categories": "TEXT", 
                          "genres": "TEXT", 
                          "release_date": "TEXT",
                          "name": "TEXT"})

    def get_games(self, steam_apps_ids: Iterable[int]) -> dict[int, dict[str]]:
        self._connect()
        
        games = {}
        
        for steam_appid in steam_apps_ids:
            
            app_data = self._get_row(steam_appid)
            
            if app_data is not None:
                
                steam_appid, description, developers, publishers, categories, genres, release_date, name = app_data
                
                game = {}
                
                game["description"] = description
                game["developers"] = developers.split(", ") if developers else []
                game["publishers"] = publishers.split(", ") if publishers else []
                game["categories"] = categories.split(", ") if categories else []
                game["genres"] = genres.split(", ") if genres else []
                game["release_date"] = release_date
                game["name"] = name
                
                games[steam_appid] = game
                
        self._close()
        return games
    
    def add_games(self, games: dict[int, dict[str]]) -> None:
        self._connect()
        
        for app_id, game in games.items():

            game["developers"] = ", ".join(game["developers"])
            game["publishers"] = ", ".join(game["publishers"])
            game["categories"] = ", ".join(game["categories"])
            game["genres"] = ", ".join(game["genres"])
            
            row = (app_id,) + tuple(game.values())
            
            self._add_row(row)
            
        self._close()