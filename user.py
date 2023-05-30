from __future__ import annotations

import os


class User:
    
    def __init__(self, steam_id: str) -> None:
        self.__steam_id: str = steam_id
        self.__user_folder: str = os.path.join("library", "data", steam_id)

    @property
    def steam_id(self) -> int:
        return self.__steam_id
    
    @property
    def user_folder(self) -> str:
        return self.__user_folder
    
    def __str__(self) -> str:
        return self.__steam_id